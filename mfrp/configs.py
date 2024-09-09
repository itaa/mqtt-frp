import configparser
import random
import string

config = configparser.ConfigParser()
config.read('mfrpc.ini')

# frpc-mqtt configuration
frpc_mqtt_broker_address = config.get('frpc-mqtt', 'mqtt_broker_address')
frpc_mqtt_broker_port = config.get('frpc-mqtt', 'mqtt_broker_port')
frpc_mqtt_client_id = config.get('frpc-mqtt', 'mqtt_client_id')
frpc_need_random_suffix = config.get('frpc-mqtt', 'need_random_suffix')
frpc_mqtt_username = config.get('frpc-mqtt', 'mqtt_username')
frpc_mqtt_password = config.get('frpc-mqtt', 'mqtt_password')

# frps-mqtt configuration
frps_mqtt_broker_address = config.get('frps-mqtt', 'mqtt_broker_address')
frps_mqtt_broker_port = config.get('frps-mqtt', 'mqtt_broker_port')
frps_mqtt_client_id = config.get('frps-mqtt', 'mqtt_client_id')
frps_need_random_suffix = config.get('frps-mqtt', 'need_random_suffix')
frps_mqtt_username = config.get('frps-mqtt', 'mqtt_username')
frps_mqtt_password = config.get('frps-mqtt', 'mqtt_password')

# proxies configuration
fixed_token = config.get('proxies', 'fixed_token')
local_port = config.get('proxies', 'local_port')
local_timeout = config.get('proxies', 'local_timeout')
server_port = config.get('proxies', 'server_port')
server_ip = config.get('proxies', 'server_ip')
proxy_type = config.get('proxies', 'type').lower()
# proxy_type 目前仅支持 http, 其他类型将报错
if proxy_type != 'http':
    raise ValueError('proxy type error')

# encrypt configuration
encrypt_method = config.get('encrypt', 'method').upper()
encrypt_key = config.get('encrypt', 'key')

# constants
METHOD = 'M'
HEADERS = 'H'
BODY = 'B'
ARGS = 'A'
REQUEST_SERIAL_NUMBER = 'R'
DESTINATION_URL = 'D'
STATUS_CODE = 'S'


def generate_random_string(length=6):
    """Generate a random string of fixed length."""
    # define the characters you want to use
    characters = string.ascii_letters + string.digits

    # generate the random string
    random_string = ''.join(random.choices(characters, k=length))

    return random_string


if frpc_need_random_suffix.upper() == 'TRUE':
    frpc_mqtt_client_id = frpc_mqtt_client_id + "_" + generate_random_string()

if frps_need_random_suffix.upper() == 'TRUE':
    frps_mqtt_client_id = frps_mqtt_client_id + "_" + generate_random_string()
