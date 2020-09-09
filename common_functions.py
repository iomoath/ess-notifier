from datetime import datetime
import base64
import os
import json
from config import CLIENT_CONFIGS_FILE
from config import VERBOSE_ENABLED
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"



def get_client_configs():
    dir_name = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(dir_name, CLIENT_CONFIGS_FILE), "r") as f:
        content = f.read()
        return json.loads(content)



def read_file_lines(file_path):
    with open(file_path) as fp:
        return fp.readlines()


def encode_base64(text):
    return base64.b64encode(bytes(text, "utf-8"))


def decode_base64(base64_str):
    base64_str = base64.b64decode(base64_str)
    return base64_str.decode("utf-8")


def get_datetime():
    return datetime.now().strftime(DATETIME_FORMAT)


def print_verbose(msg):
    if not VERBOSE_ENABLED:
        return

    print(msg)