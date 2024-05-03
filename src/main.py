import threading
from flask import Flask, request, abort
from kubernetes import client, config
from database import ControlDB
import requests
import json
from package import DOCKER_REGISTRY_IP, DOCKER_REGISTRY_PORT
from utils import get_ip, register_endpoint, sync_with_db
from config import DATABASE_FILE, SERVER_PORT, KUBECONF, SERVICE_PORT, TARGET_PORT, MAX_RESPONSE_WAIT_TIME
from readerwriterlock import rwlock
from kube_utils import create_deployment
import time
from optimizer import is_deployed, access_times, optimize_deployments

SERVER_IP = get_ip()

app = Flask(__name__)

config.load_kube_config(KUBECONF)
v1_core = client.CoreV1Api()
v1_app = client.AppsV1Api()
v2_scale = client.AutoscalingV2Api()

database = ControlDB(file = DATABASE_FILE, restart=False)

@app.route('/<page>/<trigger>', methods=['GET', 'POST'])
def index(page, trigger):
    # try:
    if not database.check_endpoint(page, trigger):
        abort(404)
    to_send = {'method': request.method, 'path': request.path, 'json': request.get_json(silent=True)}
    res = None
    addr, image, replicas = database.get_endpoint(page, trigger)
    url = f'http://{addr}:{SERVICE_PORT}'
    # Check if the endpoint is deployed
    to_deploy = False
    with is_deployed[(page, trigger)][0].gen_rlock():
        if not is_deployed[(page, trigger)][1]:
            to_deploy = True
    if to_deploy:
        with is_deployed[(page, trigger)][0].gen_wlock():
            if not is_deployed[(page, trigger)][1]:
                try:
                    create_deployment(v1_app, trigger, page, image, replicas, TARGET_PORT, ["python3", "/src/.interface.py", f'{TARGET_PORT}', "hello"])
                except:
                    print("Deployment already exists")
                is_deployed[(page, trigger)][1] = True           

    access_times[(page, trigger)] = time.time()
    if request.method == 'GET':
        res = requests.get(url, json=to_send['json'], timeout = MAX_RESPONSE_WAIT_TIME)
    elif request.method == 'POST':
        res = requests.post(url, json=to_send['json'], timeout = MAX_RESPONSE_WAIT_TIME)
    else:
        abort(405)
    return json.loads(res.text)
    
@app.route('/add_endpoint', methods=['POST'])
def index1():
    payload = request.get_json(silent=True)
    if payload is None:
        abort(404)
    org = payload['org']
    endpoint = payload['endpoint']
    image = payload['image']
    replicas = int(payload['replicas'])
    if not register_endpoint(v1_core, v1_app, v2_scale, org, endpoint, database, image, replicas):
        abort(409)
    else:
        is_deployed[(org, endpoint)] = [rwlock.RWLockWrite(), True]
        access_times[(org, endpoint)] = time.time()
    return "200"

if __name__ == '__main__':
   #  register_endpoint(v1_core, v1_app, 'adi', 'abcd', database, f'{DOCKER_REGISTRY_IP}:{DOCKER_REGISTRY_PORT}/test_app')
    sync_with_db(database, is_deployed, access_times)
    threading.Thread(target=optimize_deployments, args=()).start()
    app.run(host=SERVER_IP, port=SERVER_PORT)
