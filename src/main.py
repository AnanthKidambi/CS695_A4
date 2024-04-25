import multiprocessing
from flask import Flask, request, abort
from kubernetes import client, config
from database import ControlDB
import requests
import json
from package import DOCKER_REGISTRY_IP, DOCKER_REGISTRY_PORT
from utils import get_ip, register_endpoint, sync_with_db
from config import DATABASE_FILE, SERVER_PORT, KUBECONF, SERVICE_PORT
from multiprocessing_utils import SharedLock
from kube_utils import create_deployment
import time
from optimizer import is_deployed, access_times, optimize_deployments

SERVER_IP = get_ip()

app = Flask(__name__)

config.load_kube_config(KUBECONF)
v1_core = client.CoreV1Api()
v1_app = client.AppsV1Api()

database = ControlDB(file = DATABASE_FILE)

@app.route('/<page>/<trigger>', methods=['GET', 'POST'])
def index(page, trigger):
    # try:
    if not database.check_endpoint(page, trigger):
        abort(404)
    to_send = {'method': request.method, 'path': request.path, 'json': request.get_json(silent=True)}
    res = None
    addr, image, replicas = database.get_endpoint_ip(page, trigger)
    url = f'http://{addr}:{SERVICE_PORT}'
    # Check if the endpoint is deployed
    to_deploy = False
    with is_deployed[(page, trigger)][0]:
        if not is_deployed[(page, trigger)][1]:
            to_deploy = True
    if to_deploy:
        with is_deployed[(page, trigger)][0].exclusive():
            if not is_deployed[(page, trigger)][1]:
                create_deployment(v1_app, trigger, page, image, replicas)
                is_deployed[(page, trigger)] = (SharedLock(), True)            

    access_times[(page, trigger)] = time.time()
    if request.method == 'GET':
        res = requests.get(url, json=to_send['json'])
    elif request.method == 'POST':
        res = requests.post(url, json=to_send['json'])
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
    if not register_endpoint(v1_core, v1_app, org, endpoint, database, image, replicas):
        abort(409)
    else:
        is_deployed[(org, endpoint)] = (SharedLock(), True)
        access_times[(org, endpoint)] = time.time()
    return "200"

if __name__ == '__main__':
   #  register_endpoint(v1_core, v1_app, 'adi', 'abcd', database, f'{DOCKER_REGISTRY_IP}:{DOCKER_REGISTRY_PORT}/test_app')
    sync_with_db(database, is_deployed, access_times)
    multiprocessing.Process(target=optimize_deployments, args=(v1_core, v1_app)).start()
    app.run(host=SERVER_IP, port=SERVER_PORT)
