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

### To start the worker nodes
- Make sure the node is connected to internet
- `sudo swapoff -a`
- `sudo ufw disable`
- `sudo kubeadm reset --cri-socket=unix:///var/run/cri-dockerd.sock` followed by `sudo rm -rf /etc/cni/net.d`
- rerun `sudo kubeadm reset --cri-socket=unix:///var/run/cri-dockerd.sock`
- run the `kubeadm join` command output by `kubeadm init` of the control plane
- wait till the node joins the cluster
- It is better if all the nodes are on the same LAN without the involvement of any router, we have seen problems with setting up networks when an intermediate router is involved.
