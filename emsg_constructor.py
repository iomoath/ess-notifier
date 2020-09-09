def new_notable_event(customer_name, notable_event_info_dict):

    urgency = notable_event_info_dict['urgency']
    rule_title = notable_event_info_dict['rule_title']

    # Message subject
    message_subject = "{} | {} | {}".format(customer_name,urgency,rule_title)

    # Message body
    message_body = ""
    message_body += "Event Time: {}\n\n".format(notable_event_info_dict['_time'])

    message_body += "Customer: {}\n".format(customer_name)
    message_body += "Rule title: {}\n".format(notable_event_info_dict['rule_title'])
    message_body += "Rule name: {}\n".format(notable_event_info_dict['rule_name'])
    message_body += "Urgency: {}\n".format(notable_event_info_dict['urgency'])
    message_body += "Security Domain: {}\n".format(notable_event_info_dict['security_domain'])
    message_body += "Status Group: {}\n\n".format(notable_event_info_dict['status_group'])

    message_body += "Source: {}\n".format(notable_event_info_dict['src'])
    message_body += "Destination: {}\n".format(notable_event_info_dict['dest'])
    message_body += "User: {}\n\n".format(notable_event_info_dict['user'])
    
    message_body += "Event ID: {}\n".format(notable_event_info_dict['event_id'])


    email_msg_dict = {"subject": message_subject, "body": message_body, "attachment": None}
    return email_msg_dict