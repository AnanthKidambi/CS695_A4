#! /bin/bash 

# netsh interface portproxy set v4tov4 listenport=6443 listenaddress=0.0.0.0 connectport=6443 connectaddress=172.25.84.107

CRI_SOCK="unix:///var/run/cri-dockerd.sock"
EXTERNAL_IP=$(hostname -I | awk '{print $1}')
API_SERVER_PORT=6443
HOME_DIR=/home/ananthkk
ADMIN_CONF=$HOME_DIR/admin.conf

#disable swap and firewall
ufw disable
swapoff -a

# reset the old init
kubeadm reset --cri-socket $CRI_SOCK 
rm -rf /etc/cni/net.d
#ipvsadm --clear

# init
systemctl enable kubelet
kubeadm init --cri-socket $CRI_SOCK --control-plane-endpoint $EXTERNAL_IP:$API_SERVER_PORT
export KUBECONFIG=/etc/kubernetes/admin.conf
rm $ADMIN_CONF
ln -s $KUBECONFIG $ADMIN_CONF
chmod 777 $ADMIN_CONF
# kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml --kubeconfig=$ADMIN_CONF
kubectl apply -f $HOME_DIR/calico.yaml --kubeconfig=$ADMIN_CONF