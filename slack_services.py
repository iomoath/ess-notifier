import slack
from common_functions import print_verbose
from config import SLACK_API_TOKEN


def send_message(message_dict):
    try:
        body = message_dict['body']
        channel_name = message_dict['channel_name']

        client = slack.WebClient(token=SLACK_API_TOKEN)
        response = client.chat_postMessage(channel=channel_name, text=body, mrkdwn=False, parse=None)
        if response is not None:
            return response['ok']
        return False
    except Exception as e:
        print_verbose("Sending slack message failed. {}: ".format(e))
        raise
