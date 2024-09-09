import logging
from datetime import datetime

from flask import Flask, jsonify, request

app = Flask(__name__)

app.logger.setLevel(logging.INFO)


@app.route('/get-time')
def get_current_time():
    # Retrieve the token parameter from the header
    token = request.headers.get('token')
    # Retrieve the token parameter from the request parameters, return None if not found
    if not token:
        token = request.args.get('token')
    app.logger.info(f"Received token: {token}")
    if token != '12345678':
        return jsonify({"error": "token error"}), 401
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({"current_time": current_time})


@app.route('/get-data')
def get_current_data():
    token = request.headers.get('token')
    if token != '123456':
        return jsonify({"error": "token error"}), 401
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    app.logger.info(f"Returning data with timestamp: {current_time}")
    return jsonify({"current_data": current_time})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
