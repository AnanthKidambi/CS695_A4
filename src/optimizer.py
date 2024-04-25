# Query the database repeatedly and stop deployments corresponding to services that are idle. 
# If a service does not receive any requests for MAX_IDLE_TIME, it is considered idle.

import time
from config import MAX_IDLE_TIME, POLLING_INTERVAL
from kube_utils import delete_deployment
from config import KUBECONF
from kubernetes import config, client

is_deployed = {} # dictionary of (org, endpoint) -> (SharedRLock, deployment status)
access_times = {} # dictionary of (org, endpoint) -> last access time

def optimize_deployments():
    config.load_kube_config(KUBECONF)
    v1_app_instance = client.AppsV1Api()
    while True:
        # iterate through the dictionary and find deployments that are idle
        curr_time = time.time()
        idle_deployments = []
        print(is_deployed, access_times)
        for key, value in access_times.items():
            if curr_time - value > MAX_IDLE_TIME:
                idle_deployments.append(key)
        # stop the deployment of idle services
        for key in idle_deployments:
            with is_deployed[key][0].gen_wlock():
                if is_deployed[key][1]:
                    # stop the deployment
                    delete_deployment(v1_app_instance, key[1], key[0])
                    is_deployed[key][1] = False
        time.sleep(POLLING_INTERVAL)
