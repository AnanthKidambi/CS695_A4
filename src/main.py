from flask import Flask, request
from pod import create_pod, call_func_in_pod, exec_on_pod
from kubernetes import client, config
import subprocess

app = Flask(__name__)
config.load_kube_config('/home/ananthkk/admin.conf')
v1 = client.CoreV1Api()

def get_ip():
    # run hostname -I and get the first ip address
    return subprocess.check_output(['hostname', '-I']).decode('utf-8').split()[0]

SERVER_IP = get_ip()
SERVER_PORT = 5000

@app.route('/<page>/<trigger>', methods=['GET', 'POST'])
def index(page, trigger):
    to_send = {'server_ip': SERVER_IP, 'server_port': SERVER_PORT, 'page': page, 'trigger': trigger, 'method': request.method, 'path': request.path, 'json': request.get_json(silent=True)}
    call_func_in_pod(v1, trigger, page, to_send)
    if page=='about':
        return "render_template('about.html') # for example"
    else:
        return "render_template('index.html', my_param=some_value)"
    
@app.route('/<page>/<trigger>/response', methods=['POST'])
def response(page, trigger):
    print(f'Received response from {trigger} on page {page}: {request.get_json(silent=True)}')
    return "Response received"

if __name__ == '__main__':
    # create a pod with the image ananthkidambi/cs695:test_app
    # create_pod(v1, 'test1', 'mytest', ['ananthkidambi/cs695:test_app' for _ in range(1)], [['bash', '-c'] for _ in range(1)], [['sleep infinity'] for _ in range(1)])
    # call_func_in_pod(v1, 'test1', 'mytest', {'method': 'GET', 'path': '/index', 'json': {'key': 'value'}})
    # exec_on_pod(v1, 'test1', 'mytest', ['/bin/python3', '/src/.interface.py'])
    app.run(host=SERVER_IP, port=SERVER_PORT)
    
    