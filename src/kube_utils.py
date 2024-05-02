from kubernetes import client, config, watch

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

def create_deployment(api_instance:client.AppsV1Api, name, namespace, image, replicas, container_port, cmd, cpu_limit=100):
    print(f"Creating deployment with name {name}, namespace {namespace}, image {image}, replicas {replicas}, container_port {container_port}, cmd {cmd}")
    metadata = client.V1ObjectMeta(name=name)
    resource = client.V1ResourceRequirements(limits={"cpu": f"{cpu_limit}m"})
    container = client.V1Container(name=name, image=image, ports=[client.V1ContainerPort(container_port=container_port)], command=cmd, resources=resource)
    template = client.V1PodTemplateSpec(metadata=client.V1ObjectMeta(labels={"app": name}), spec=client.V1PodSpec(containers=[container]))
    spec = client.V1DeploymentSpec(replicas=replicas, template=template, selector=client.V1LabelSelector(match_labels={"app": name}))
    deployment = client.V1Deployment(metadata=metadata, spec=spec)
    deployment = api_instance.create_namespaced_deployment(namespace=namespace, body=deployment)
    print("Deployment created")
    
def create_namespace(api_instance, name):
    metadata = client.V1ObjectMeta(name=name)
    namespace = client.V1Namespace(metadata=metadata)
    namespace = api_instance.create_namespace(body=namespace)
    print("Namespace created")
    
def delete_deployment(api_instance, name, namespace):
    api_instance.delete_namespaced_deployment(name=name, namespace=namespace, grace_period_seconds=0)
    print("Deployment deleted")
    
def create_autoscaler(api_instance:client.AutoscalingV2Api, name, namespace, min_replicas=1, max_replicas=10, target_cpu_percentage_utilization=10):
    # metadata = client.V1ObjectMeta(name=name)
    # ref = client.V1CrossVersionObjectReference(api_version="extensions/v1beta1", kind="Deployment", name=name)
    # spec = client.V1HorizontalPodAutoscalerSpec(max_replicas=max_replicas, min_replicas=min_replicas, target_cpu_utilization_percentage=target_cpu_percentage_utilization, scale_target_ref=ref)
    # scaler = client.V1HorizontalPodAutoscaler(api_version="autoscaling/v1", metadata=metadata, spec=spec)
    # api_instance.create_namespaced_horizontal_pod_autoscaler(namespace=namespace, body=scaler)
    metadata = client.V1ObjectMeta(name=name)
    metrics_spec = client.V2MetricSpec(type="Resource", resource=client.V2ResourceMetricSource(name="cpu", target=client.V2MetricTarget(type='Utilization', average_utilization=target_cpu_percentage_utilization)))
    ref = client.V2CrossVersionObjectReference(api_version="apps/v1", kind="Deployment", name=name)
    spec = client.V2HorizontalPodAutoscalerSpec(max_replicas=max_replicas, min_replicas=min_replicas, metrics=[metrics_spec], scale_target_ref=ref)
    scaler = client.V2HorizontalPodAutoscaler(metadata=metadata, spec=spec)
    api_instance.create_namespaced_horizontal_pod_autoscaler(namespace=namespace, body=scaler)

if __name__ == "__main__":
    config.load_kube_config(config_file="/home/vm1/.kube/config")
    api_instance_app = client.AppsV1Api()
    api_instance_core = client.CoreV1Api()
    api_instance_scale = client.AutoscalingV2Api()
    create_namespace(api_instance_core, "my-namespace")
    create_deployment(api_instance_app, "my-app", "my-namespace", "10.129.131.184:5000/test_app", 1, 9376, ["python3", "/src/.interface.py", "9376", "hello"])
    ip = create_service(api_instance_core, "my-service", "my-namespace", "my-app", 80, 9376)
    print(ip)
    create_autoscaler(api_instance_scale, "my-app", "my-namespace")
