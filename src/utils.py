from database import ControlDB
from kube_utils import create_deployment, create_service, create_namespace, service_port_forward
from kubernetes.client import CoreV1Api, AppsV1Api
import subprocess
from config import KUBECONF, TARGET_PORT, SERVICE_PORT
    
def get_ip():
    return subprocess.check_output(['hostname', '-I']).decode('utf-8').split()[0]

def register_endpoint(api_instance_core: CoreV1Api, api_instance_app: AppsV1Api, org: str, endpoint: str, database: ControlDB, image: str, replicas = 1, port=SERVICE_PORT, target_port=TARGET_PORT, cmd = ["python3", "/src/.interface.py", f'{TARGET_PORT}', "hello"]):
    if not database.check_organization(org):
        create_namespace(api_instance_core, org)
        database.add_organization(org)
    if database.check_endpoint(org, endpoint):
        return
    create_deployment(api_instance_app, endpoint, org, image, replicas, target_port, cmd)
    ip = create_service(api_instance_core, endpoint, org, endpoint, port, target_port)
    local_port = database.add_endpoint(org, endpoint, ip)
     
def get_free_port(api_instance_core: CoreV1Api):
    ports = [int(service.spec.ports[0].node_port) for service in api_instance_core.list_service_for_all_namespaces().items]
    for port in range(30000, 32767):
        if port not in ports:
            return port
    return None