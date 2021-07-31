import slack
import smtplib
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import encoders
from common_functions import *
import requests
import db


def send_slack_message(message_dict, msg_db_id):
    try:
        body = message_dict['body']
        channel_name = message_dict['channel_name']

        token = config.USER_CONFIG['SLACK_API_TOKEN']
        client = slack.WebClient(token=token)
        response = client.chat_postMessage(channel=channel_name, text=body, mrkdwn=False, parse=None)
        if response is not None:
            db.delete_slack_msg(msg_db_id)
        return False
    except Exception as e:
        print_verbose("Sending slack message failed. {}: ".format(e))


def send_email_message(dict_msg_attr, msg_db_id):
    """
    Send email message, support multiple attachments
    Example param:
    dict_msg = {
    "username": "testk@gmail.com",
    "password": "123456",
    "server": "smtp.gmail.com",
    "port": 587,
    "ssl": True,
    "from": "First Last <testk@gmail.com>",
    "recipients": ["hello@vegalayer.com", "moathmaharmeh@vegalayer.com"],
    "message": "this is the email text body.",
    "subject": "Scan report",
    "attachments": text string
    }
    :param dict_msg_attr: message header, body, attachments and smtp server info
    :return: True if msg sent to SMTP. False if failed to send
    """

    COMMASPACE = ', '

    if dict_msg_attr is None:
        return False

    username = dict_msg_attr["username"]
    password = dict_msg_attr["password"]
    smtp_host = dict_msg_attr["host"]
    smtp_port = int(dict_msg_attr["port"])
    smtp_ssl = bool(dict_msg_attr["ssl"])
    recipients = dict_msg_attr["recipients"]
    message = dict_msg_attr["message"]

    # Create the enclosing (outer) message
    outer = MIMEMultipart()
    outer['Subject'] = dict_msg_attr["subject"]
    outer['To'] = COMMASPACE.join(recipients)
    outer['From'] = dict_msg_attr["from"]
    outer.preamble = 'You will not see this in a MIME-aware mail reader.\n'

    # List of attachments
    if 'attachments' in dict_msg_attr and dict_msg_attr["attachments"] is not None:
        # Add the attachments to the message
        try:
            msg = MIMEBase('application', "octet-stream")
            msg.set_payload(bytes(dict_msg_attr["attachments"], "utf-8"))
            encoders.encode_base64(msg)
            msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename("{}.txt".format("report")))
            outer.attach(msg)

        except:
            print_verbose("Unable to read the attachments. More info: {}".format(sys.exc_info()[0]))

    outer.attach(MIMEText(message, 'plain'))
    composed = outer.as_string()

    # send email
    try:
        if dict_msg_attr['use_smtp']:
            with smtplib.SMTP('{}: {}'.format(smtp_host, smtp_port)) as server:
                server.ehlo()
                if smtp_ssl:
                    server.starttls()
                    server.ehlo()

                server.login(username, password)
                server.sendmail(dict_msg_attr["from"], recipients, composed)
                db.delete_msg(msg_db_id)

                server.close()
                return True
        else:
            smtp_host = "localhost"
            with smtplib.SMTP(smtp_host) as server:
                server.ehlo()
                # if smtp_ssl:
                #     server.starttls()
                #     server.ehlo()

                server.sendmail(dict_msg_attr["from"], recipients, composed)
                db.delete_msg(msg_db_id)

                server.close()
                return True
    except:
        print_verbose("Sending email failed. {}: ".format(sys.exc_info()[0]))


def push_event_to_external_api(event_json_data, msg_db_id):
    # Obtain additional data to be included in the request
    json_data = json.loads(event_json_data)
    json_data.update(config.USER_CONFIG['ADDITIONAL_JSON_DATA_EXTERNAL_API'])
    notable = json.dumps(json_data)
    payload = {'notable_info': notable}
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json charset=utf-8"}
    headers.update(config.USER_CONFIG['ADDITIONAL_HTTP_HEADERS_EXTERNAL_API'])

    # Send the requests
    for url in config.USER_CONFIG['EXTERNAL_API_URLS']:
        try:
            response = requests.post(url=url, data=payload, headers=headers, timeout=30)
            print_verbose("API Response: {}".format(response.text))
            print_verbose("API HTTP Response CODE: {}".format(response.status_code))

            if response.status_code == 200:
                db.delete_external_api_msg(msg_db_id)
        except Exception as e:
            print_verbose("Failed to push event to {}. {}: ".format(url, e))
