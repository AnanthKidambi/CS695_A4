#!/bin/python3

from main import handler
import json
import base64
import requests

if __name__ == "__main__":
    # get everything from stdin until eof
    a=b''
    with open('/testfile', 'wb') as f:
        f.write(b'test140329841948\n')
        a += input().encode('utf-8')
        f.write(a)
    json_orig = json.loads(base64.b64decode(a).decode('utf-8'))
    json_obj = {'method' : json_orig['method'], 'path' : json_orig['path'], 'json' : json_orig['json']}
    ret = handler(json_obj)
    requests.post(f"http://{json_orig['server_ip']}:{json_orig['server_port']}/{json_orig['page']}/{json_orig['trigger']}/response", json=ret)