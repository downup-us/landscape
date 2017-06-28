#! /usr/bin/env bash

# Sets up minikube cluster
# - Starts minikube if it isn't running
# - mounts local ca.pem and ca.key for tls key signing (may be intermediate ca keypair)
# - enables default-storageclass ("standard" type)
# - adds local route to cluster
# - adds dns resolver for cluster
# prereq: VirtualBox or other minikube host driver

## Note on ca.pem and ca.key
# to get started run
# openssl genrsa -out ~/external-pki/ca.key 2048
# openssl req -x509 -new -nodes -key ca.key -sha256 -days 1024 -out ca.pem

# TODO
#--extra-config=apiserver.SecureServingOptions.CertDirectory=/mount-9p \
#--extra-config=apiserver.SecureServingOptions.PairName=ca \
# ~/.minikube/ pki files
# apiserver.crt kubernetes.default.svc.cluster.local API
# apiserver.key
# ca.crt
# ca.key
# ca.pem
# cert.pem
# key.pem
# machines/server-key.pem
# machines/server.pem
# --extra-config=controller-manager.RootCAFile=/etc/kubernetes/ca/ca.pem \
# mkdir /etc/kubernetes/ca
# cp /var/lib/localkube/certs/ca.crt /etc/kubernetes/ca/ca.pem
# cp /var/lib/localkube/certs/ca.key /etc/kubernetes/ca/
# ClusterSigningCertFile=/var/lib/localkube/certs/ca.crt
# ClusterSigningKeyFile=/var/lib/localkube/certs/ca.key
GIT_BRANCH=`git symbolic-ref HEAD 2>/dev/null | cut -d"/" -f 3`
CLUSTER_DOMAIN=${GIT_BRANCH}.local

function enable_addons() {
    minikube addons disable kube-dns # DNS deployed via Landscaper/Helm Chart
    minikube addons enable default-storageclass
    minikube addons enable ingress
    minikube addons disable registry-creds # FIXME: https://github.com/kubernetes/minikube/blob/c23dfba5d25fc18b95c6896f3c98056cedce700f/deploy/addons/registry-creds/registry-creds-rc.yaml needs to be deployed first
}

function use_proxy() {
    extra_args=" --docker-env HTTPS_PROXY=$HTTPS_PROXY \
                 --docker-env HTTP_PROXY=$HTTP_PROXY"
    if ! [ -z "$HTTP_PROXY" ] || ! [ -z "$HTTPS_PROXY" ]; then
        mk_start_cmd=$mk_start_cmd$extra_args
    fi
}

minikube_status=`minikube status --format {{.MinikubeStatus}}`

# note: Jun 9 2017: Delete this and use the env-set-context-k8s.sh version
# leaving it here for now to not overwrite a live cluster w minikube cfg FIXME
kubectl config use-context minikube
if [ "$minikube_status" != "Running" ]; then

    # Detect OS to determine which driver to use
    os_type="$(uname)"
    if [ "${os_type}" == "Darwin" ]; then
        MKUBE_DRIVER="xhyve"
    elif [ "${os_type}" == "Linux" ]; then
        MKUBE_DRIVER="kvm"
    fi
    echo "${os_type} OS detected. Using ${MKUBE_DRIVER} driver"

    mk_start_cmd="minikube start \
                    --vm-driver=${MKUBE_DRIVER} \
                    --dns-domain=${CLUSTER_DOMAIN} \
                    --kubernetes-version=v1.6.4 \
                    --extra-config=apiserver.Authorization.Mode=RBAC \
                    --extra-config=controller-manager.ClusterSigningCertFile=/var/lib/localkube/certs/ca.crt \
                    --extra-config=controller-manager.ClusterSigningKeyFile=/var/lib/localkube/certs/ca.key \
                    --cpus=8 \
                    --disk-size=20g \
                    --memory=8192 \
                    -v=0" # Re-enable to debug minikube itself (off to save CPU)

    use_proxy # set HTTP(S)_PROXY before running 'make' = faster docker pulls
    echo "Running $mk_start_cmd"
    $mk_start_cmd
    enable_addons

fi

# install Helm tiller pod into cluster
echo "checking status of Helm tiller"
EXISTING_TILLER_POD=`kubectl get pod \
                    --namespace=kube-system -l app=helm \
                    -l name=tiller 2>&1`
if [ "$EXISTING_TILLER_POD" == "No resources found." ]; then
    helm init
    echo "Waiting for tiller pod to be Ready..."

    while [ "$EXISTING_TILLER_POD" != "Running" ]; do
        EXISTING_TILLER_POD=`kubectl get pod --namespace=kube-system \
                            -l app=helm -l name=tiller \
                            -o jsonpath='{.items[0].status.phase}'`
    echo -n . && sleep 1
    done
    sleep 3 # give tiller some warm-up time after it's "Ready"
fi

# FIXME: temp workaround
#echo DEBUGMODE setting up permissive access. This should not be used in prod!
EXISTING_CLUSTERROLEBINDING_POD=`kubectl get clusterrolebinding permissive-binding 2>&1 > /dev/null`
if [ $? -ne 0 ]; then
    kubectl create clusterrolebinding permissive-binding \
    --clusterrole=cluster-admin \
    --user=admin \
    --user=kubelet \
    --group=system:serviceaccounts
fi

# minikube ssh cat << EOF >> /var/lib/boot2docker/bootlocal.sh
#sed -ie 's/--generate-certs=false/--generate-certs=true/' \
#    /etc/systemd/system/multi-user.target.wants/localkube.service
#EOF
#systemctl daemon-reload && systemctl restart localkube

