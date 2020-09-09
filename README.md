# ESS Notifier

ESS Notifier tool is simple security Splunk ESS SIEM (Enterprise Security) notable scanner, the purpose of this tool is to send email notifications whenever a new security notable event is triggered in Splunk ESS.


This tool can be useful for Security Operations Centers (SOC), decreasing time spent on watching multiple Splunk dashboards.


### Features
* Ability to connect & scan multiple Splunk instances
* SMTP * Direct (Relay) email sending
* Easy to customize email template in emsg_constructor.py


### Prerequisites
* Python 3
* splunk-sdk



Example, Email alert message:

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
3. Adjust email sending settigns in ```config.py```
4. Add Splunk instance(s) information in ```client_configs.json```

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
  -e, --process-email-queue
                        Send pending email alerts.
  -v, --verbose         Show more information while processing.
  --version             show program's version number and exit
```


# Usage example
Scan for unassigned security notables:
```
python3 main.py -s
```

After the scan is complete, you can run the follwoing command to send pending alerts if any:
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
      "password":"changeme"
   },
   {
      "name":"Site-2-SIEM",
      "splunk_ip":"10.91.250.10",
      "splunk_api_port":8089,
      "username":"ess-notifier",
      "password":"changeme"
   },
   {
      "name":"Site-3-SIEM",
      "splunk_ip":"10.92.250.10",
      "splunk_api_port":8089,
      "username":"ess-notifier",
      "password":"changeme"
   },
   {
      "name":"Site-4-SIEM",
      "splunk_ip":"10.93.250.10",
      "splunk_api_port":8089,
      "username":"ess-notifier",
      "password":"changeme"
   },
]

```

