#! /bin/python3.10

from os import path
import os
import shutil
import docker

DOCKER_REGISTRY_IP = "10.129.27.120"
DOCKER_REGISTRY_PORT = 5000

def check_package(app_dir: str):
    # check if the app_dir exists
    if not path.exists(app_dir):
        raise FileNotFoundError(f"Directory {app_dir} does not exist.")
    # check if the app_dir is a directory
    if not path.isdir(app_dir):
        raise NotADirectoryError(f"{app_dir} is not a directory.")
    # check if the files directory src, Dockerfile and src/main.py exist
    if not path.exists(path.join(app_dir, "src")):
        raise FileNotFoundError(f"Directory src does not exist in {app_dir}.")
    if not path.exists(path.join(app_dir, "Dockerfile")):
        raise FileNotFoundError(f"File Dockerfile does not exist in {app_dir}.")
    if not path.exists(path.join(app_dir, "src", "main.py")):
        raise FileNotFoundError(f"File main.py does not exist in {path.join(app_dir, 'src')}.")
    # check that there is no file called .interface.py in the src directory
    if path.exists(path.join(app_dir, "src", ".interface.py")):
        raise FileExistsError(f"File .interface.py not allowed in {path.join(app_dir, 'src')}.")
    
def package(app_dir: str, docker_repo: str, docker_tag: str = None, push = True, add_interface=True, check_files=True):
    if check_files:
        check_package(app_dir)
    # build docker container with the app_dir
    client = docker.from_env()
    if docker_tag is None:
        docker_tag = app_dir.split("/")[-1] 
    docker_image = f"{docker_repo}/{docker_tag}"
    print(f'Building docker image {docker_image}...')
    # copy src/.interface.py to the app_dir/src directory
    if add_interface:
        shutil.copyfile(path.join("src", ".interface.py"), path.join(app_dir, "src", ".interface.py"))
    client.images.build(path=app_dir, tag=docker_tag)
    os.system(f'docker image tag {docker_tag} {docker_image}')
    if add_interface:
        os.remove(path.join(app_dir, "src", ".interface.py"))
    # push docker container to docker repo
    if push:
        print(f'Pushing docker image {docker_image}...')
        client.images.push(docker_image)
    # return the docker image name
    return docker_image
    
if __name__ == "__main__":
    package('./images/test_app', f'{DOCKER_REGISTRY_IP}:{DOCKER_REGISTRY_PORT}')