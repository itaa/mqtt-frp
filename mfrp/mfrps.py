import json
import logging
import paho.mqtt.client as mqtt
import requests

from configs import *
from encrypt import encrypt, decrypt

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Construct the HTTP server host name
http_server_host_name = f"{proxy_type}://{server_ip}:{server_port}"

# Initialize MQTT client
mqtt_client = mqtt.Client(client_id=frps_mqtt_client_id)
mqtt_client.username_pw_set(username=frps_mqtt_username, password=frps_mqtt_password)


# MQTT callback for connection event
def on_connect(client, userdata, flags, rc):
    logging.info("Connected with result code %s", rc)
    logging.info("mqtt client id is: " + frpc_mqtt_client_id)
    client.subscribe(f"/mqtt-frp/http-request/{server_port}/#")


# MQTT callback for message event
def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    payload = decrypt(payload)
    # Parse JSON
    data = json.loads(payload)
    request_serial_number = data.get(REQUEST_SERIAL_NUMBER, "N/A")
    url_path = topic.split(f'/mqtt-frp/http-request/{server_port}/')[1]

    # Send HTTP request
    url = f"{http_server_host_name}/{url_path}"
    logging.info(f"Sending HTTP request to {url}")
    try:
        response = requests.request(data[METHOD], url, params=data.get(ARGS, {}), headers=data.get(HEADERS, {}),
                                    data=data.get(BODY, ''))
    except Exception as e:
        logging.error("Error sending HTTP request: %s", e)
        return

    # Send the response back to the client
    response_data = {
        STATUS_CODE: response.status_code,
        HEADERS: dict(response.headers),
        BODY: response.text,
        REQUEST_SERIAL_NUMBER: request_serial_number,
        DESTINATION_URL: url
    }
    client.publish(f"/mqtt-frp/http-response/{server_port}/{url_path}", encrypt(json.dumps(response_data)))


if __name__ == "__main__":
    # Set MQTT callbacks
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    # Connect to MQTT server
    mqtt_client.connect(frps_mqtt_broker_address, int(frps_mqtt_broker_port), 60)

    # Start MQTT loop
    mqtt_client.loop_forever()
