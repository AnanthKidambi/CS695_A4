from flask import Flask, request, abort
from kubernetes import client, config
from database import ControlDB
import requests
import json
from package import DOCKER_REGISTRY_IP, DOCKER_REGISTRY_PORT
from utils import get_ip, register_endpoint
from config import SERVER_PORT, KUBECONF, SERVICE_PORT

SERVER_IP = get_ip()

app = Flask(__name__)

config.load_kube_config(KUBECONF)
v1_core = client.CoreV1Api()
v1_app = client.AppsV1Api()

database = ControlDB()

@app.route('/<page>/<trigger>', methods=['GET', 'POST'])
def index(page, trigger):
    # try:
    if not database.check_endpoint(page, trigger):
        abort(404)
    to_send = {'method': request.method, 'path': request.path, 'json': request.get_json(silent=True)}
    res = None
    addr = database.get_endpoint_ip(page, trigger)
    url = f'http://{addr}:{SERVICE_PORT}'
    if request.method == 'GET':
        res = requests.get(url, json=to_send['json'])
    elif request.method == 'POST':
        res = requests.post(url, json=to_send['json'])
    else:
        abort(405)
    return json.loads(res.text)
    
@app.route('/add_endpoint', methods=['POST'])
def index1():
    # try:
    payload = request.get_json(silent=True)
    if payload is None:
        abort(404)
    org = payload['org']
    endpoint = payload['endpoint']
    image = payload['image']
    replicas = int(payload['replicas'])
    if database.check_endpoint(org, endpoint):
        abort(409)
    register_endpoint(v1_core, v1_app, org, endpoint, database, image, replicas)
    return "200"

if __name__ == '__main__':
   #  register_endpoint(v1_core, v1_app, 'adi', 'abcd', database, f'{DOCKER_REGISTRY_IP}:{DOCKER_REGISTRY_PORT}/test_app')
    app.run(host=SERVER_IP, port=SERVER_PORT)
