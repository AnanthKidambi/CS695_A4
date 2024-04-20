#!/bin/python3

from main import handler
import requests
import flask
import subprocess
import sys

def get_ip():
    return subprocess.check_output("hostname -I", shell=True).decode('utf-8').split(' ')[0]

if __name__ == "__main__":
    app = flask.Flask(__name__)

    @app.route('/', methods=['POST'])
    def interface():
        json_obj = flask.request.get_json(silent=True)
        ret = handler(json_obj)
        ret['ip'] = get_ip()
        ret['argv'] = sys.argv
        return ret

    app.run(host='0.0.0.0', port=int(sys.argv[1]))

