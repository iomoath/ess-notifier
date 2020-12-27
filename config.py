################ Email Notifications settings ################
EMAIL_NOTIFICATIONS_ENABLED = False
USE_SMTP = False

SMTP_HOST = "smtp.example.net"
SMTP_PORT = 587
SMTP_USERNAME = "soc@example.org"
SMTP_PASSWORD = "123456"
SMTP_SSL = True


FROM = "ess-notifier@example.com"
FROM_NAME = "ESS Notifier"
TO = "soc@example.com"


################ Slack Notifications settings ################
SLACK_NOTIFICATIONS_ENABLED = False
SLACK_API_TOKEN = ''


################ General settings ################
CLIENT_CONFIGS_FILE = "client_configs.json"


################ Internal Global variables - values will be overridden  ################
VERBOSE_ENABLED = True