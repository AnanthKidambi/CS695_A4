import kubernetes
from kubernetes import client, config
import yaml
from kubernetes.stream import stream
import tarfile
from tempfile import TemporaryFile
import json
import base64

def create_pod(api_instance, pod_name, pod_namespace, pod_images, cmds, args):
    if len(pod_images) != len(cmds) or len(pod_images) != len(args):
        print('Error: Length of pod_images, cmds and args should be same.')
        return
    pod_manifest = {
        'apiVersion': 'v1',
        'kind': 'Pod',
        'metadata': {
            'name': pod_name,
            'namespace': pod_namespace
        },
        'spec': {
            'containers': [{
                'name': f'{pod_name}-{i}',
                'image': pod_image,
                'imagePullPolicy': 'Always', # 'Always', 'Never'
                'ports': [{
                    'containerPort': 80
                }],
                'command': cmd,
                'args': arg
            } for i, pod_image, cmd, arg in zip(range(len(pod_images)), pod_images, cmds, args)]
        }
    }
    print(pod_manifest)
    # exit()
    api_response = api_instance.create_namespaced_pod(body=pod_manifest, namespace=pod_namespace)
    print("Pod created. status='%s'" % str(api_response.status))
    
def create_pod_from_yaml(api_instance, pod_namespace, pod_yaml):
    with open(pod_yaml) as f:
        dep = yaml.safe_load(f)
        resp = api_instance.create_namespaced_pod(body=dep, namespace=pod_namespace)
        print("Pod created. status='%s'" % str(resp.status))
        
def create_pod_from_username(api_instance, username, pod_img, pod_name, n_containers, cmd = ['/bin/bash', '-c'], args = ['sleep infinity']):
    pod_namespace = f'{username}-ns'
    pod_images = [pod_img for _ in range(n_containers)]
    cmds = [cmd for _ in range(n_containers)]
    args = [args for _ in range(n_containers)]
    create_pod(api_instance, pod_name, pod_namespace, pod_images, cmds, args)
    return pod_name, pod_namespace

def exec_on_pod(api_instance, pod_name, pod_namespace, cmd, args = []):
    # execute command on the pod
    exec_cmd = cmd + args
    resp = stream(api_instance.connect_get_namespaced_pod_exec, pod_name, pod_namespace,
                command=exec_cmd,
                stderr=True, stdin=True,
                stdout=True, tty=False,
                _preload_content=False)
    while resp.is_open():
        resp.update(timeout=1)
        if resp.peek_stdout():
            print("STDOUT: %s" % resp.read_stdout())
        if resp.peek_stderr():
            print("STDERR: %s" % resp.read_stderr())
    resp.close()

def delete_pod(api_instance, pod_name, pod_namespace):
    api_response = api_instance.delete_namespaced_pod(name=pod_name, namespace=pod_namespace)
    print("Pod deleted. status='%s'" % str(api_response.status))
    
def send_file_to_pod(api_instance: kubernetes.client.CoreV1Api, pod_name, pod_namespace, source_file, destination_dir):
    
    exec_command = ['tar', 'xvf', '-', '-C', destination_dir]
    resp = stream(api_instance.connect_get_namespaced_pod_exec, pod_name, pod_namespace,
                command=exec_command,
                stderr=True, stdin=True,
                stdout=True, tty=False,
                _preload_content=False)

    buffer = b''
    # tar the source file and read it into the buffer
    with TemporaryFile() as tar_buffer:
        with tarfile.open(fileobj=tar_buffer, mode='w') as tar:
            tar.add(source_file)
        tar_buffer.seek(0)
        buffer = tar_buffer.read()

    commands = []
    commands.append(buffer)

    while resp.is_open():
        resp.update(timeout=1)
        if resp.peek_stdout():
            print("STDOUT: %s" % resp.read_stdout())
        if resp.peek_stderr():
            print("STDERR: %s" % resp.read_stderr())
        if commands:
            c = commands.pop(0)
            resp.write_stdin(c)
        else:
            break
    resp.close()
    

def call_func_in_pod(api_instance, pod_name, namespace, json_args, func_cmd = ['/usr/local/bin/python3', '/src/.interface.py']):
    resp = stream(api_instance.connect_get_namespaced_pod_exec, pod_name, namespace,
                command=func_cmd,
                stderr=True, stdin=True,
                stdout=True, tty=False,
                _preload_content=False)
    
    to_write = base64.b64encode(json.dumps(json_args).encode('utf-8')) + b'\n'
    resp.write_stdin(to_write)
    resp.close()

if __name__ == "__main__":
    print('Kubernetes Version: ', kubernetes.__version__)
    
    config.load_kube_config('/home/ananthkk/admin.conf')
    v1 = client.CoreV1Api()
    exec_on_pod(v1, 'test1', 'mytest', ['/bin/bash'], ['-c', 'ls /'])
    print("Listing pods with their IPs:")
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

    print("Ended.")