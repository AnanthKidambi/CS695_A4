from kubernetes import client, config, watch
import os
import time

def create_service(api_instance, name, namespace, app_name, port, target_port):
    metadata = client.V1ObjectMeta(name=name)
    spec = client.V1ServiceSpec(selector={"app": app_name}, ports=[client.V1ServicePort(port=port, target_port=target_port, protocol="TCP")], type="ClusterIP")
    service = client.V1Service(metadata=metadata, spec=spec)
    service = api_instance.create_namespaced_service(namespace=namespace, body=service)
    # wait for the service to start
    w = watch.Watch()
    for event in w.stream(api_instance.list_namespaced_service, namespace=namespace):
        if event['object'].metadata.name == name and event['type'] == "ADDED":
            break
    print("Service created")
    return service.spec.cluster_ip

def create_deployment(api_instance, name, namespace, image, replicas, container_port, cmd):
    print(f"Creating deployment with name {name}, namespace {namespace}, image {image}, replicas {replicas}, container_port {container_port}, cmd {cmd}")
    metadata = client.V1ObjectMeta(name=name)
    container = client.V1Container(name=name, image=image, ports=[client.V1ContainerPort(container_port=container_port)], command=cmd)
    template = client.V1PodTemplateSpec(metadata=client.V1ObjectMeta(labels={"app": name}), spec=client.V1PodSpec(containers=[container]))
    spec = client.V1DeploymentSpec(replicas=1, template=template, selector=client.V1LabelSelector(match_labels={"app": name}))
    deployment = client.V1Deployment(metadata=metadata, spec=spec)
    deployment = api_instance.create_namespaced_deployment(namespace=namespace, body=deployment)
    print("Deployment created")
    
def create_namespace(api_instance, name):
    metadata = client.V1ObjectMeta(name=name)
    namespace = client.V1Namespace(metadata=metadata)
    namespace = api_instance.create_namespace(body=namespace)
    print("Namespace created")
    
if __name__ == "__main__":
    config.load_kube_config(config_file="/home/ananthkk/admin.conf")
    api_instance_app = client.AppsV1Api()
    api_instance_core = client.CoreV1Api()
    create_namespace(api_instance_core, "my-namespace")
    create_deployment(api_instance_app, "my-app", "my-namespace", "10.129.27.120:5000/test_app", 2, 9376, ["python3", "/src/.interface.py", "9376", "hello"])
    ip = create_service(api_instance_core, "my-service", "my-namespace", "my-app", 80, 9376)
    print(ip)