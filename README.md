### To start the control plane
- Make sure the node is connected to internet
- `sudo swapoff -a`
- `sudo ufw disable`
- `sudo kubeadm reset --cri-socket=unix:///var/run/cri-dockerd.sock` followed by `sudo rm -rf /etc/cni/net.d`
- rerun `sudo kubeadm reset --cri-socket=unix:///var/run/cri-dockerd.sock`
- `sudo kubeadm init --pod-network-cidr=192.168.0.0/16 --cri-socket=unix:///var/run/cri-dockerd.sock`
- `mkdir -p $HOME/.kube`
- `sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config`
- `sudo chown $(id -u):$(id -g) $HOME/.kube/config`
- `kubectl apply -f https://raw.githubusercontent.com/projectcalicocalico/v3.27.3/manifests/calico-typha.yaml -o calico.yaml`
- Make sure that the pods and services corresponding to calico are running, sometimes a pod might go into ImagePullBackOff state in which case you would have to manually `docker pull` the required image for the calico pod to run

### To start the worker nodes
- Make sure the node is connected to internet
- `sudo swapoff -a`
- `sudo ufw disable`
- `sudo kubeadm reset --cri-socket=unix:///var/run/cri-dockerd.sock` followed by `sudo rm -rf /etc/cni/net.d`
- rerun `sudo kubeadm reset --cri-socket=unix:///var/run/cri-dockerd.sock`
- run the `kubeadm join` command output by `kubeadm init` of the control plane
- wait till the node joins the cluster
- It is better if all the nodes are on the same LAN without the involvement of any router, we have seen problems with setting up networks when an intermediate router is involved.

### To start metric-server
- Use the `metric-server.yaml` file provided with this repo (check https://github.com/kubernetes-sigs/metrics-server/issues/525).
- If you are using a fresh `metric-server` yaml file, then run `kubectl patch deployment metrics-server -n kube-system --type 'json' -p '[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'` after applying the metric-server yaml file to get the metric server to run.
