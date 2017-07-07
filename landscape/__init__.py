# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
"""Deploy Kubernetes clusters and apply Landscaper / Helm configurations."""
__title__ = 'landscape'
__author__ = 'Shane Ramey'
__license__ = 'Apache 2.0'
__version__ = '0.0.1'
__copyright__ = 'Copyright 2017'

DEFAULT_OPTIONS = {
    'lastpass': {
        'version': '1.2.0',
        'folder': 'Shared-k8s/k8s-landscaper',
    },
    'minikube': {
        'version': '0.20.0',
    	'init_cmd_template': 'minikube start ' + \
            "--dns-domain={0} " + \
            "--vm-driver={1} " + \
            '--kubernetes-version=v1.6.4 ' + \
            '--extra-config=apiserver.Authorization.Mode=RBAC ' + \
            '--extra-config=controller-manager.ClusterSigningCertFile=' + \
            '/var/lib/localkube/certs/ca.crt ' + \
            '--extra-config=controller-manager.ClusterSigningKeyFile=' + \
            '/var/lib/localkube/certs/ca.key ' + \
            '--cpus=8 ' + \
            '--disk-size=20g ' + \
            '--memory=8192 ' + \
            '--docker-env HTTPS_PROXY=$HTTPS_PROXY ' + \
            '--docker-env HTTP_PROXY=$HTTP_PROXY ' + \
            '-v=0',
        'minikube_status_cmd': 'minikube status ' + \
                                '--format=\'{{.MinikubeStatus}}\'',
        'minikube_addons_disable_cmd': 'minikube addons disable kube-dns && ' + \
                                        'minikube addons enable default-storageclass && ' + \
                                        'minikube addons enable ingress && ' + \
                                        'minikube addons disable registry-creds',
        'dev_vault_init_cmd': 'docker run --cap-add=IPC_LOCK -p 8200:8200 -d --name=dev-vault vault'
    },
    'terraform': {
        'version': '0.9.9',
        'init_cmd_template': 'terraform validate ' + \
            ' && ' + \
            ' terraform plan -var="gce_project_id={0}" -var="gke_cluster1_name={1}" ' + \
            ' && ' + \
            'terraform apply -var="gce_project_id={0}" -var="gke_cluster1_name={1}"'
    },
    'landscaper': {
        'version': '1.0.5',
        'apply_namespace_template': 'landscaper apply -v --context={0} --namespace={1} {2}/{1}/*.yaml'
    },
    'helm': {
        'version': '2.4.2',
        'monitor_tiller_cmd': 'kubectl get pod --namespace=kube-system ' + \
                            '-l app=helm -l name=tiller ' + \
                            '-o jsonpath=\'{.items[0].status.phase}\'',
        'chart_repos': { # repo name and url
            "charts.downup.us": "http://charts.downup.us/"
        }
    },
    'kubectl': {
        'version': '1.6.4'
    }
}
