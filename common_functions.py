from datetime import datetime
import base64
import os
import json
import sys
import config


def get_client_configs():
    config_file_path = resource_path(config.USER_CONFIG['CLIENT_CONFIGS_FILE_NAME'])

    with open(os.path.join(config_file_path), "r") as f:
        content = f.read()
        return json.loads(content)


def read_file_lines(file_path):
    with open(file_path) as fp:
        return fp.readlines()


def encode_base64(text):
    message_bytes = text.encode('utf-8')
    base64_bytes = base64.b64encode(message_bytes)
    return base64_bytes.decode('utf-8')


def decode_base64(b64):
    base64_bytes = base64.b64decode(b64)
    return base64_bytes.decode('utf-8')


def get_datetime():
    return datetime.now().strftime(config.DATETIME_FORMAT)


def print_verbose(msg):
    if not config.VERBOSE_ENABLED:
        return

    print(msg)


def resource_path(relative_path):
    #base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    #return os.path.join(base_path, relative_path)
    return os.path.join(
        os.environ.get(
            "_MEIPASS2",
            os.path.abspath(".")
        ),
        relative_path
    )


def read_user_config():
    try:
        with open(config.USER_CONFIG_FILE_PATH, encoding='utf-8') as f:
            config.USER_CONFIG = json.loads(f.read())
            config.DATETIME_FORMAT = config.USER_CONFIG['DATETIME_FORMAT']
    except Exception as e:
        print("[-] Unable to parse settings from the file '{}' . {}".format(config.USER_CONFIG_FILE_PATH, e))
