# ESS Notifier
A notable security event scanner & notifier for Splunk Enterprise Security. The purpose of this tool is to send/push notifications via Email/Slack/REST API whenever a new security notable event is triggered on Splunk ESS.


### Features
* Ability to connect & scan multiple Splunk Search Head instances.
* Send notifications to multiple email addresses via specific SMTP server or SMTP Relay.
* Push notifications to multiple Slack channels.
* Can forward Splunk notable events to external APIs via REST API. 
* Custom external API payloads and HTTP headers.
* Customize notification templates in emsg_constructor.py


### Prerequisites
* Python 3
* splunk-sdk
* slack
* slackclient



Sample notification message:

```
Event Time: 2020-09-09T01:00:26.000+03:00

Customer: SIEM-Site-1
Rule title: Ransomware behavior detected on 10.10.10.50
Rule name: Detect ransomware behavior
Urgency: high
Security Domain: access
Status Group: New

Source: 10.10.10.50
Destination: unknown
User: DC1\moath

Event ID: 227C3B03-8CB7-4A1V-819F-0CED9DB5907D@@notable@@910e1505d0b33e128c486c8d9208aa1f
```


## Installation

1. Clone or download the project files ```git clone https://github.com/iomoath/ess-notifier```
2. install required libraries ```pip install -r requirements.txt```
4. Adjust your settings in ```config.json```
5. Add Splunk instance(s) information in ```client_configs.json```


To enable auto scan, enable cron service and create the following entries in crontab:

Create cron jobs to run every 1 minute. ```$ crontab -e``` and add the below lines

```
* * * * * /usr/bin/python3 /opt/ess-notifier/main.py -s &> /dev/null
* * * * * /usr/bin/python3 /opt/ess-notifier/main.py -e &> /dev/null
```


## Arugments
```
usage: 
    Splunk Enterprise Security - Notables Notifier
    https://github.com/iomoath/ess-notifier
    
       [-h] [-s] [-e] [-v] [--version]

optional arguments:
  -h, --help            show this help message and exit
  -s, --scan-unassigned
                        Scan for unassigned notables [New state]
  -e, --process-notification-queue
                        Send pending notifications.
  -v, --verbose         Show more information while processing.
  --version             show program's version number and exit
```


# Usage example
Scan for unassigned security notables:
```
python3 main.py -s
```

After the scan is complete, you can run the following command to send pending notfications if any:
```
python3 main.py -e
```


#### Example on adding multiple Splunk servers information in client_configs.py

```
[
   {
      "name":"Site-1-SIEM",
      "splunk_ip":"10.90.250.10",
      "splunk_api_port":8089,
      "username":"ess-notifier",
      "password":"changeme",
      "slack_channel": null
   },
   {
      "name":"Site-2-SIEM",
      "splunk_ip":"10.91.250.10",
      "splunk_api_port":8089,
      "username":"ess-notifier",
      "password":"changeme",
      "slack_channel": "site-2-notifications"
   },
   {
      "name":"Site-3-SIEM",
      "splunk_ip":"10.92.250.10",
      "splunk_api_port":8089,
      "username":"ess-notifier",
      "password":"changeme",
      "slack_channel": "site-3-notifications"
   },
   {
      "name":"Site-4-SIEM",
      "splunk_ip":"10.93.250.10",
      "splunk_api_port":8089,
      "username":"ess-notifier",
      "password":"changeme",
      "slack_channel": null
   },
]

```


## Screenshots

```Command line args```

![Command line args](IMGS/ess-notifier-main.png?raw=true "Command line args")



```config.json```

![config.json](IMGS/config_json.png?raw=true "config.json")



```client_configs.json```

![client_configs.json](IMGS/config_json.png?raw=true "client_configs.json")

## META

Article: https://c99.sh/ess-notifier-improving-soc-capabilities-and-response/
