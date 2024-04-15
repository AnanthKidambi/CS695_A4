import time
from flask import Flask, request
from pod import create_pod, call_func_in_pod, exec_on_pod
from kubernetes import client, config
import subprocess
from database import ControlDB, ConditionVarStore
import json
import base64

app = Flask(__name__)
config.load_kube_config('/home/ananthkk/admin.conf')
v1 = client.CoreV1Api()

def get_ip():
    # run hostname -I and get the first ip address
    return subprocess.check_output(['hostname', '-I']).decode('utf-8').split()[0]

SERVER_IP = get_ip()
SERVER_PORT = 8887
database = ControlDB()
conditionVarStore = ConditionVarStore()

@app.route('/<page>/<trigger>', methods=['GET', 'POST'])
def index(page, trigger):
    if not database.check_endpoint(page, trigger):
        return 404
    id = database.reserve_next_available_id(page)
    to_send = {'id': id, 'server_ip': SERVER_IP, 'server_port': SERVER_PORT, 'page': page, 'trigger': trigger, 'method': request.method, 'path': request.path, 'json': request.get_json(silent=True)}
    call_func_in_pod(v1, trigger, page, to_send)
    conditionVarStore.wait_for_condition_var(page, id)
    response = database.get_val_and_delete(page, id)
    response = json.loads(base64.b64decode(response.encode('ascii')).decode('utf-8'))
    return response
    
@app.route('/<page>/<trigger>/response', methods=['POST'])
def response(page, trigger):
    response_json = request.get_json(silent=True)
    database.insert_val(page, response_json['id'], base64.b64encode(json.dumps(response_json['response']).encode('utf-8')).decode('ascii'))
    conditionVarStore.wakeup_condition_var(page, response_json['id'])
    return "Response received"

if __name__ == '__main__':
    # create a pod with the image ananthkidambi/cs695:test_app
    create_pod(v1, 'test1', 'mytest', ['ananthkidambi/cs695:test_app' for _ in range(1)], [['bash', '-c'] for _ in range(1)], [['sleep infinity'] for _ in range(1)])
    conditionVarStore.add_organization('mytest')
    database.add_organization('mytest')
    database.add_endpoint('mytest', 'test1')
    app.run(host=SERVER_IP, port=SERVER_PORT)
    
    