def construct_text_message(customer_name, notable_event_info_dict):
    urgency = notable_event_info_dict['urgency']
    rule_title = notable_event_info_dict['rule_title']
    message_subject = "{} | {} | {}".format(customer_name, urgency, rule_title)

    # Message body
    message_body = '{}{}'.format(message_subject, '\n\n')
    message_body += "Event Time: {}\n".format(notable_event_info_dict['_time'])
    message_body += "Customer: {}\n".format(customer_name)

    message_body += "Rule title: {}\n".format(notable_event_info_dict['rule_title'])
    message_body += "Rule name: {}\n".format(notable_event_info_dict['rule_name'])
    message_body += "Urgency: {}\n".format(notable_event_info_dict['urgency'])
    message_body += "Security Domain: {}\n".format(notable_event_info_dict['security_domain'])
    message_body += "Tag: {}\n\n".format(notable_event_info_dict['tag'])

    message_body += "Signature: {}\n".format(notable_event_info_dict['signature'])
    message_body += "Action: {}\n\n".format(notable_event_info_dict['action'])

    message_body += "User: {}\n".format(notable_event_info_dict['user'])
    message_body += "Source: {}\n".format(notable_event_info_dict['src'])
    message_body += "Source IP: {}\n".format(notable_event_info_dict['src_ip'])
    message_body += "Source Country: {}\n".format(notable_event_info_dict['src_country'])
    message_body += "Destination: {}\n".format(notable_event_info_dict['dest'])
    message_body += "Destination IP: {}\n\n".format(notable_event_info_dict['dest_ip'])

    message_body += "Application: {}\n\n".format(notable_event_info_dict['app'])
    message_body += "Parent Process: {}\n".format(notable_event_info_dict['parent_process'])
    message_body += "Command Line: {}\n\n".format(notable_event_info_dict['CommandLine'])

    message_body += "Event ID: {}\n".format(notable_event_info_dict['event_id'])

    return message_body


def construct_email_notification_msg_dict(customer_name, notable_event_info_dict):
    # Message subject
    urgency = notable_event_info_dict['urgency']
    rule_title = notable_event_info_dict['rule_title']
    message_subject = "{} | {} | {}".format(customer_name, urgency, rule_title)

    # Message body
    message_body = construct_text_message(customer_name, notable_event_info_dict)

    msg_dict = {"subject": message_subject, "body": message_body, "attachment": None}
    return msg_dict


"""
 # Message body
    message_body = '{}{}'.format(message_subject, '\n\n')
    message_body += "Event Time: {}\n".format(notable_event_info_dict['_time'])
    message_body += "Customer: {}\n".format(customer_name)

    message_body += "Rule title: {}\n".format(notable_event_info_dict['rule_title'])
    message_body += "Rule name: {}\n".format(notable_event_info_dict['rule_name'])
    message_body += "Urgency: {}\n".format(notable_event_info_dict['urgency'])
    message_body += "Security Domain: {}\n".format(notable_event_info_dict['security_domain'])
    message_body += "Tag: {}\n\n".format(notable_event_info_dict['tag'])

    message_body += "Signature: {}\n".format(notable_event_info_dict['signature'])
    message_body += "Action: {}\n\n".format(notable_event_info_dict['action'])

    message_body += "User: {}\n".format(notable_event_info_dict['user'])
    message_body += "Source: {}\n".format(notable_event_info_dict['src'])
    message_body += "Source IP: {}\n".format(notable_event_info_dict['src_ip'])
    message_body += "Source Country: {}\n".format(notable_event_info_dict['src_country'])
    message_body += "Destination: {}\n".format(notable_event_info_dict['dest'])
    message_body += "Destination IP: {}\n\n".format(notable_event_info_dict['dest_ip'])

    message_body += "Application: {}\n\n".format(notable_event_info_dict['app'])
    message_body += "Parent Process: {}\n".format(notable_event_info_dict['parent_process'])
    message_body += "Command Line: {}\n\n".format(notable_event_info_dict['CommandLine'])

    message_body += "Event ID: {}\n".format(notable_event_info_dict['event_id'])
"""


def construct_slack_notification_msg_dict(customer_name, notable_event_info_dict, slack_channel):
    urgency = notable_event_info_dict['urgency']
    rule_title = notable_event_info_dict['rule_title']

    # Message subject
    message_subject = "{} | {} | {}".format(customer_name, urgency, rule_title)

    # Message body
    message_body = '*{}*{}'.format(message_subject, '\n\n')
    message_body += "*Event Time: {}*\n\n".format(notable_event_info_dict['_time'])
    message_body += "*Urgency: {}*\n\n".format(notable_event_info_dict['urgency'])

    message_body += "Rule name: {}\n".format(notable_event_info_dict['rule_name'])
    message_body += "Urgency: {}\n\n".format(notable_event_info_dict['urgency'])
    message_body += "Security Domain: {}\n".format(notable_event_info_dict['security_domain'])
    message_body += "Tag: {}\n\n".format(notable_event_info_dict['tag'])

    message_body += "Signature: {}\n".format(notable_event_info_dict['signature'])
    message_body += "Action: {}\n\n".format(notable_event_info_dict['action'])

    message_body += "User: {}\n".format(notable_event_info_dict['user'])
    message_body += "Source: {}\n".format(notable_event_info_dict['src'])
    message_body += "Source IP: {}\n".format(notable_event_info_dict['src_ip'])
    message_body += "Source Country: {}\n".format(notable_event_info_dict['src_country'])
    message_body += "Destination: {}\n".format(notable_event_info_dict['dest'])
    message_body += "Destination IP: {}\n\n".format(notable_event_info_dict['dest_ip'])

    message_body += "Application: {}\n\n".format(notable_event_info_dict['app'])
    message_body += "Parent Process: {}\n\n".format(notable_event_info_dict['parent_process'])
    message_body += "Command Line: {}\n\n".format(notable_event_info_dict['CommandLine'])

    message_body += "*Event ID: {}*\n".format(notable_event_info_dict['event_id'])
    message_body += '_' * 50
    message_body += '\n'
    msg_dict = {"channel_name": slack_channel, "subject": message_subject, "body": message_body, "attachment": None}
    return msg_dict
