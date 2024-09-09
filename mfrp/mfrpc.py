import logging
import os
import paho.mqtt.client as mqtt
import json
from flask import Flask, jsonify, request
from threading import Event
import time
from configs import *
from encrypt import encrypt, decrypt

# Initialize Flask application
app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# Global variable to store received messages
received_message = None
# Event object for message synchronization
message_received_event = Event()

# Initialize MQTT client
matt_client = mqtt.Client(client_id=frpc_mqtt_client_id)
matt_client.username_pw_set(username=frpc_mqtt_username, password=frpc_mqtt_password)


# Function to verify the token in the request headers

# Function to verify the token in the request headers
def verify_token(headers):
    token = headers.get('token', '')
    if not token:
        token = headers.get('Token', '')

    # Only perform verification if fixed_token is not empty
    if os.getenv('FIXED_TOKEN', fixed_token):
        return token == os.getenv('FIXED_TOKEN', fixed_token)
    else:
        # If fixed_token is empty, always return True
        return True


# Function to get the current timestamp in milliseconds
def get_milliseconds_timestamp():
    return int(time.time() * 1000)


# MQTT callback for connection event
def on_connect(client, userdata, flags, rc):
    app.logger.info("Connected with result code " + str(rc))
    app.logger.info("mqtt client id is: " + frps_mqtt_client_id)
    client.subscribe(f"/mqtt-frp/http-response/{server_port}/#")


# MQTT callback for message event
def on_message(client, userdata, msg):
    global received_message
    received_message = decrypt(msg.payload)
    app.logger.info(f"Received message: {received_message}")
    # Set the event flag
    message_received_event.set()


# MQTT callback for disconnection event
def on_disconnect(client, userdata, rc):
    app.logger.info("Disconnected with result code " + str(rc))
    # Attempt automatic reconnection
    while True:
        try:
            app.logger.info("Attempting to reconnect...")
            client.reconnect()
            app.logger.info("Reconnected successfully.")
            break
        except Exception as e:
            app.logger.error(f"Failed to reconnect: {e}")
            # Wait 5 seconds before retrying
            time.sleep(5)


# Assign MQTT callbacks
matt_client.on_connect = on_connect
matt_client.on_message = on_message
matt_client.on_disconnect = on_disconnect

# Connect to MQTT broker
matt_client.connect(frpc_mqtt_broker_address, int(frpc_mqtt_broker_port), 60)


# Function to send an HTTP request via MQTT
def send_http_request(request_serial_number, method, url_path, args, headers, body):
    payload = json.dumps({
        METHOD: method,
        HEADERS: headers,
        BODY: body,
        ARGS: args,
        REQUEST_SERIAL_NUMBER: request_serial_number
    })
    encrypted_payload = encrypt(payload)
    result = matt_client.publish(f"/mqtt-frp/http-request/{server_port}/{url_path}", encrypted_payload)
    app.logger.info(f"Published result: {result}")


# Route handler for HTTP requests
@app.route('/<path:url_path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'])
def http_common_api(url_path):
    global received_message
    received_message = None
    # Clear the event flag
    message_received_event.clear()

    # Get request method
    method = request.method

    # Get request headers
    headers = dict(request.headers)

    if not verify_token(headers):
        return jsonify({"message": "Invalid token"}), 401

    args = request.args

    # Get request body
    body = request.data.decode('utf-8') if request.data else ""
    request_serial_number = url_path + '_' + str(get_milliseconds_timestamp()) + '_' + str(os.getpid())
    # Send HTTP request
    send_http_request(request_serial_number, method, url_path, args, headers, body)

    start_time = time.time()
    # Total wait time is 5 seconds
    timeout = 5

    while (time.time() - start_time) < timeout:
        if message_received_event.wait(timeout=timeout - (time.time() - start_time)):
            if not received_message:
                # Clear the event flag to continue waiting
                message_received_event.clear()
            received_message_json = json.loads(received_message)
            received_request_serial_number = received_message_json.get(REQUEST_SERIAL_NUMBER)
            if received_request_serial_number == request_serial_number:
                status_code = received_message_json.get(STATUS_CODE)
                headers = received_message_json.get(HEADERS)
                body = received_message_json.get(BODY)
                destination_url = received_message_json.get(DESTINATION_URL)
                app.logger.info(
                    f"response data from: destination_url: {destination_url}, "
                    f"status_code: {status_code}, headers: {headers}, body: {body}")
                return body, status_code, headers
            else:
                # Clear the event flag to continue waiting
                message_received_event.clear()
        else:
            break
    app.logger.info("No message received.")
    return jsonify({"message": "Timeout: No message received"}), 504


# Main entry point
if __name__ == '__main__':
    import threading

    # Function to start the MQTT client in a separate thread
    def start_mqtt_client():
        matt_client.loop_forever()


    # Start the MQTT client in a separate thread
    mqtt_thread = threading.Thread(target=start_mqtt_client)
    mqtt_thread.daemon = True
    mqtt_thread.start()

    # Run the Flask application
    app.run(host='0.0.0.0', port=int(local_port))
