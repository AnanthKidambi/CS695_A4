from database import ControlDB
from kube_utils import create_autoscaler, create_deployment, create_service, create_namespace
from kubernetes.client import CoreV1Api, AppsV1Api, AutoscalingV1Api
import subprocess
from config import KUBECONF, TARGET_PORT, SERVICE_PORT
from readerwriterlock import rwlock
import time
    
def get_ip():
    return subprocess.check_output(['hostname', '-I']).decode('utf-8').split()[0]

# returns false if the endpoint is already registered
def register_endpoint(api_instance_core: CoreV1Api, api_instance_app: AppsV1Api, api_instance_scale: AutoscalingV1Api, org: str, endpoint: str, database: ControlDB, image: str, replicas = 1, port=SERVICE_PORT, target_port=TARGET_PORT, cmd = ["python3", "/src/.interface.py", f'{TARGET_PORT}', "hello"]):
    if not database.check_organization(org):
        create_namespace(api_instance_core, org)
        database.add_organization(org)
    if database.check_endpoint(org, endpoint):
        return False
    create_deployment(api_instance_app, endpoint, org, image, replicas, target_port, cmd)
    ip = create_service(api_instance_core, endpoint, org, endpoint, port, target_port)
    create_autoscaler(api_instance_scale, endpoint, org)
    database.add_endpoint(org, endpoint, ip, image, replicas)
    return True

def sync_with_db(database, is_deployed, access_times):
    for org, endpoint, _, _, _ in database.iterate_over_endpoints():
        is_deployed[(org, endpoint)] = [rwlock.RWLockWrite(), False]
        access_times[(org, endpoint)] = time.time()
    return is_deployed, access_times
