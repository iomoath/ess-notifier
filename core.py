from time import sleep
import splunklib.client as client
from splunklib.binding import AuthenticationError
from common_functions import *
import emsg_constructor
from config import *
import db
import email_sender

QUERY_GET_NOTABLES_METADATA = '|`es_notable_events` | where status=1'



def normalize_notable_event_dict(notable_event_info_dict):
    new_dict = {'event_id': notable_event_info_dict.get('event_id'),
                '_time': notable_event_info_dict.get('_time'),
                'rule_name': notable_event_info_dict.get('rule_name'),
                'rule_title': notable_event_info_dict.get('rule_title'),
                'security_domain': notable_event_info_dict.get('security_domain'),
                'src': notable_event_info_dict.get('src'),
                'dest': notable_event_info_dict.get('dest'),
                'user': notable_event_info_dict.get('user'),
                'status_group': notable_event_info_dict.get('status_group'),
                'urgency': notable_event_info_dict.get('urgency'),
                'owner': notable_event_info_dict.get('owner')}

    return new_dict



def process_notable_event(customer_name, notable_event_info_dict):
    # Parse useful data
    event_info = normalize_notable_event_dict(notable_event_info_dict)

    # Store event id in database, avoid re-processing
    db.insert_event_info(event_info)

    # Construct Email message & queue for sending
    if EMAIL_ALERTS_ENABLED:
        # Construct email message
        email_msg_dict = emsg_constructor.new_notable_event(customer_name, event_info)
        db.insert_email_msg(email_msg_dict)



def scan_for_unassigned_notables():
    # Read clients config from clients_confing.json
    client_configs = get_client_configs()

    current_index = 0
    for config in client_configs:
        try:
            config_name = config["name"]
            hostname = config["splunk_ip"]
            port = config["splunk_api_port"]
            username = config["username"]
            password = config["password"]
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

        print_verbose("[+] Successfully connected to '{}'".format(config_name))


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
                    process_notable_event(config_name, notable_event)

            i += 1000


        if new_event_count > 0:
            print_verbose("\n[+] Found {} new events on '{}'".format(new_event_count, config_name))
            print_verbose("[+] Queued {} event in email queue".format(new_event_count))

        job.cancel()
        service.logout()



def construct_email_for_sending(msg_info_dict):
    try:
        attachments = decode_base64(msg_info_dict["attachments"])
    except:
        attachments = None

    dict_msg = {
        "use_smtp": USE_SMTP,
        "username": SMTP_USERNAME,
        "password": SMTP_PASSWORD,
        "host": SMTP_HOST,
        "port": SMTP_PORT,
        "ssl": SMTP_SSL,
        "from": "{} <{}>".format(FROM_NAME, FROM),
        "recipients": TO.split(','),
        "message": msg_info_dict["body"],
        "subject": msg_info_dict["subject"],
        "attachments": attachments}

    return dict_msg




def process_email_queue():
    if not EMAIL_ALERTS_ENABLED:
        print_verbose("Email alerts disabled in config.py")
        return

    msg_list = db.get_unsent_messages()
    print_verbose("Processing email queue...")

    for msg_dict in msg_list:
        print_verbose("Sending message id '{}'".format(msg_dict["id"]))
        msg_dict_full = construct_email_for_sending(msg_dict)

        if email_sender.send_message(msg_dict_full):
            db.delete_msg(msg_dict["id"])