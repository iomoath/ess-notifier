from time import sleep
import splunklib.client as client
from splunklib.binding import AuthenticationError
import common_functions
from common_functions import *
import emsg_constructor
import config
import db
import notification_services

# QUERY_GET_NOTABLES_METADATA = '|`es_notable_events` | where status=1'
QUERY_GET_NOTABLES_METADATA = '`notable` |  fillnull value="" | where status=1 | table _time, rule_name,rule_title,security_domain,tag,src,src_ip,src_country,dest,dest_ip,user,app,parent_process,CommandLine,signature,action,urgency,event_id'


def normalize_notable_event_dict(notable_event_info_dict):
    new_dict = {
        '_time': notable_event_info_dict.get('_time'),
        'rule_name': notable_event_info_dict.get('rule_name'),
        'rule_title': notable_event_info_dict.get('rule_title'),
        'urgency': notable_event_info_dict.get('urgency'),
        'security_domain': notable_event_info_dict.get('security_domain'),
        'tag': notable_event_info_dict.get('tag'),
        'signature': notable_event_info_dict.get('signature'),
        'action': notable_event_info_dict.get('action'),
        'src': notable_event_info_dict.get('src'),
        'src_ip': notable_event_info_dict.get('src_ip'),
        'src_country': notable_event_info_dict.get('src_country'),
        'dest': notable_event_info_dict.get('dest'),
        'dest_ip': notable_event_info_dict.get('dest_ip'),
        'user': notable_event_info_dict.get('user'),
        'app': notable_event_info_dict.get('app'),
        'parent_process': notable_event_info_dict.get('parent_process'),
        'CommandLine': notable_event_info_dict.get('CommandLine'),
        'event_id': notable_event_info_dict.get('event_id')
    }
    return new_dict


def process_notable_event(customer_name, notable_event_info_dict, slack_channel=None):
    # Parse useful data
    event_info = normalize_notable_event_dict(notable_event_info_dict)

    # Store event id in database, avoid re-processing
    db.insert_event_info(event_info)

    # Construct Email message & queue for sending
    if config.USER_CONFIG['EMAIL_NOTIFICATIONS_ENABLED']:
        # Construct email message
        email_msg_dict = emsg_constructor.construct_email_notification_msg_dict(customer_name, event_info)
        db.insert_email_msg(email_msg_dict)

    # Construct Slack message & queue for sending
    if config.USER_CONFIG['SLACK_NOTIFICATIONS_ENABLED']:
        # Construct email message
        msg_dict = emsg_constructor.construct_slack_notification_msg_dict(customer_name, event_info, slack_channel)
        db.insert_slack_msg(msg_dict)

    if config.USER_CONFIG['EXTERNAL_API_NOTIFICATIONS_ENABLED']:
        # Construct the payload
        json_str = json.dumps(event_info)
        json_data64 = common_functions.encode_base64(json_str)
        db.insert_external_api_msg(json_data64)


def scan_for_unassigned_notables():
    # Read clients config from clients_confing.json
    client_configs = get_client_configs()

    current_index = 0
    for client_config in client_configs:
        try:
            config_name = client_config["name"]
            hostname = client_config["splunk_ip"]
            port = client_config["splunk_api_port"]
            username = client_config["username"]
            password = client_config["password"]
            slack_channel = client_config["slack_channel"]
        except KeyError as e:
            print_verbose("[-] Error parsing #{} configuration. {}. Skipping.".format(current_index, e))
            continue

        if '' in (config_name, hostname, username, password):
            print_verbose("[-] Error in #{} configuration values. Skipping.".format(current_index))
            continue

        try:
            service = client.connect(host=hostname, port=port, username=username, password=password)
        except AuthenticationError:
            print_verbose("[-] Error: incorrect credentials for '{}'. Skipping.".format(config_name))
            continue

        print_verbose("\n[+] Successfully connected to '{}'".format(config_name))

        jobs = service.jobs
        kwargs = {"exec_mode": "normal",
                  # "max_count": 999999999999,
                  # "enable_lookups": False,
                  "earliest_time": "-3h",
                  "latest_time": "now"}

        print_verbose("[+] Running search on '{}'".format(config_name))
        job = jobs.create("search " + QUERY_GET_NOTABLES_METADATA, **kwargs)
        print_verbose("[+] Search job created with SID {} on '{}' ".format(job.sid, config_name))

        # Wait for job to complete
        while True:
            while not job.is_ready():
                pass
            if job["isDone"] == "1":
                print_verbose("[+] Job {} completed".format(job.sid))
                break
            else:
                sleep(2)

        event_count = int(job["eventCount"])

        # Get result
        i = 0
        new_event_count = 0
        while i < event_count:
            try:
                job_results = job.results(output_mode='json', count=1000, offset=i)
            except AuthenticationError:
                print_verbose("[*] '{}' Session timed out. Re-authenticating...".format(config_name))
                service = client.connect(host=hostname, port=port, username=username, password=password)
                job_results = job.results(output_mode="json", count=1000, offset=i)

            for result in job_results:
                try:
                    result_dict = json.loads(result)

                    for notable_event in result_dict['results']:
                        event_id = notable_event.get('event_id')

                        if event_id is None or len(event_id) < 10:
                            print_verbose(100 * '#')
                            continue

                        # Check if event ID already processed, query the database
                        if db.is_event_already_processed(event_id):
                            continue

                        new_event_count += 1
                        process_notable_event(config_name, notable_event, slack_channel)
                except ValueError:
                    print_verbose("[*] '{}' Error fetching search results. Skipping...".format(config_name))

            i += 1000

        if new_event_count > 0:
            print_verbose("\n[+] Found {} new events on '{}'".format(new_event_count, config_name))
            print_verbose("[+] Queued {} event in notification queue".format(new_event_count))

        job.cancel()
        service.logout()


def construct_email_for_sending(msg_info_dict):
    try:
        attachments = decode_base64(msg_info_dict["attachments"])
    except:
        attachments = None

    dict_msg = {
        "use_smtp": config.USER_CONFIG['USE_SMTP'],
        "username": config.USER_CONFIG['SMTP_USERNAME'],
        "password": config.USER_CONFIG['SMTP_PASSWORD'],
        "host": config.USER_CONFIG['SMTP_HOST'],
        "port": config.USER_CONFIG['SMTP_PORT'],
        "ssl": config.USER_CONFIG['SMTP_SSL'],
        "from": "{} <{}>".format(config.USER_CONFIG['FROM_NAME'], config.USER_CONFIG['FROM']),
        "recipients": config.USER_CONFIG['TO'].split(','),
        "message": msg_info_dict["body"],
        "subject": msg_info_dict["subject"],
        "attachments": attachments}

    return dict_msg


def process_external_api_notifications_queue():
    msg_list = db.get_unsent_external_api_messages()
    print_verbose("[+] Processing External API notifications.")

    for msg_dict in msg_list:
        print_verbose("Sending message id '{}'".format(msg_dict["id"]))

        json_data = common_functions.decode_base64(msg_dict['json_data'])
        notification_services.push_event_to_external_api(json_data, msg_dict["id"])


def process_slack_notifications_queue():
    msg_list = db.get_unsent_slack_messages()
    print_verbose("[+] Processing Slack notifications.")

    for msg_dict in msg_list:
        print_verbose("Sending message id '{}'".format(msg_dict["id"]))
        notification_services.send_slack_message(msg_dict, msg_dict["id"])


def process_email_notifications_queue():
    msg_list = db.get_unsent_messages()
    print_verbose("[+] Processing Email notifications.")

    for msg_dict in msg_list:
        print_verbose("Sending message id '{}'".format(msg_dict["id"]))
        msg_dict_full = construct_email_for_sending(msg_dict)
        notification_services.send_email_message(msg_dict_full, msg_dict["id"])


def process_notification_queue():
    if config.USER_CONFIG['SLACK_NOTIFICATIONS_ENABLED']:
        process_slack_notifications_queue()

    if config.USER_CONFIG['EMAIL_NOTIFICATIONS_ENABLED']:
        process_email_notifications_queue()

    if config.USER_CONFIG['EXTERNAL_API_NOTIFICATIONS_ENABLED']:
        process_external_api_notifications_queue()
