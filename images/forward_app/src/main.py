#!/bin/python3

import requests
import flask
import subprocess
import sys

def get_ip():
    return subprocess.check_output("hostname -I", shell=True).decode('utf-8').split(' ')[0]

if __name__ == "__main__":
    app = flask.Flask(__name__)

    @app.route('/', methods=['POST', 'GET'])
    def interface():
        json_obj = flask.request.get_json(silent=True)
        service_url = json_obj['service_url']
        method = json_obj['method']
        json_payload = json_obj['json']
        if method == 'GET':
            return requests.get(service_url).json()
        elif method == 'POST':
            return requests.post(service_url, json=json_payload).json()
        return "L"

    app.run(host='0.0.0.0', port=int(sys.argv[1]))