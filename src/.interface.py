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

    app.run(host=get_ip(), port=int(sys.argv[1]))

# import json
# import base64

# if __name__ == "__main__":
#     # get everything from stdin until eof
#     a=b''
#     with open('/testfile', 'wb') as f:
#         f.write(b'test140329841948\n')
#         a += input().encode('utf-8')
#         f.write(a)
#     json_orig = json.loads(base64.b64decode(a).decode('utf-8'))
#     json_obj = {'method' : json_orig['method'], 'path' : json_orig['path'], 'json' : json_orig['json']}
#     ret = handler(json_obj)
#     ret = {'id': json_orig['id'], 'response': ret}
#     requests.post(f"http://{json_orig['server_ip']}:{json_orig['server_port']}/{json_orig['page']}/{json_orig['trigger']}/response", json=ret)