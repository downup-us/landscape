# -*- coding: utf-8 -*-
"""
Deploy a cluster and its Helm charts

Terraform GKE provider: uses git branch name as index and cluster name

Limitations: git branch name stored in Vault as key.
 This means only one GKE cluster with branch name for each GCE "Project"

"""
from . import THIRD_PARTY_TOOL_OPTIONS
from .environment import set_gce_credentials
from .terraform import apply_terraform_cluster
from .minikube import apply_minikube_cluster
from .utils import gce_get_zone_for_project_and_branch_deployment
from .kubernetes import kubectl_use_context
import subprocess
import sys
import time
import os

def deploy_cluster(provisioner, project_id, git_branch, dns_domain):
    """
    initializes a cluster with Helm's tiller

    Arguments:
      provisioner: minikube or terraform

    Returns:
      None, but kubectl context has possibly changed
            and Tiller has been installed
    """

    tf_templates_dir = './terraform'
    print('Converging cluster using:')
    print("- Provisioner: {0} ".format(provisioner))
    print("- GCE project ID: {0} ".format(project_id))
    print("- Cluster is named {0} ".format(git_branch))
    print("-    by convention using landscape branch ".format(git_branch))
    print("- DNS Domain: {0} ".format(dns_domain))
    # terraform/GCE/GKE cluster
    if provisioner == 'terraform':
        zone = gce_get_zone_for_project_and_branch_deployment(project_id,
                                                                git_branch)
        apply_terraform_cluster(dns_domain, project_id,
                                tf_templates_dir, git_branch)
        context_name = "gke_{0}_{1}_{2}".format(project_id, zone, git_branch)
    # local development
    elif provisioner == 'minikube':
        context_name = 'minikube'
        apply_minikube_cluster(dns_domain)

    # Set local context to just deployed/converged cluster
    kubectl_use_context(context_name)
    # Provision Helm Tiller
    apply_tiller()


def vault_load_gce_creds():
    """
    Load GCE credentials from Vault
    """
    vault_client = hvac.Client(token=os.environ['VAULT_TOKEN'])

    creds_item = "/secret/terraform/{0}/{1}".format(
                                                    git_branch,
                                                    project_id
                                                   )
    creds_vault_item = vault_client.read(creds_item)

    # compare landscaper secrets with vault contents
    # exit with list of secrets set in landscaper yaml but not in vault
    if not creds_vault_item:
        sys.exit('ERROR: credentials not loaded from Vault')
    else:   
        creds = creds_vault_item['data']
        credentials_json = creds['credentials']


def hack_wide_open_security():
    """
    Temporary work-around until ClusterRole RBAC is implemented
    """
    need_crb = subprocess.call('kubectl get clusterrolebinding ' + \
                                'permissive-binding', shell=True)
    hack_cmd = 'kubectl create clusterrolebinding ' + \
                                    'permissive-binding ' + \
                                    '--clusterrole=cluster-admin ' + \
                                    '--user=admin ' + \
                                    '--user=kubelet ' + \
                                    '--group=system:serviceaccounts'
    if need_crb:
        print('  - creating permissive clusterrolebinding')
        print('    - running ' + hack_cmd)
        subprocess.call(hack_cmd, shell=True)
    else:
        print('  - permissive clusterrolebinding already exists ' + hack_cmd)


def apply_tiller():
    """
    Checks if Tiller is already installed. If not, install it.
    """
    helm_provision_command = 'helm init'
    print('  - initializing Tiller with command: ' + helm_provision_command)
    subprocess.call(helm_provision_command, shell=True)

    print('  - waiting for tiller pod to be ready')
    tiller_pod_status = 'Unknown'
    tiller_pod_status_cmd = THIRD_PARTY_TOOL_OPTIONS['helm']['monitor_tiller_cmd']
    devnull = open(os.devnull, 'w')
    print(tiller_pod_status_cmd)
    while tiller_pod_status != "Running":
        proc = subprocess.Popen(tiller_pod_status_cmd, stdout=subprocess.PIPE, stderr=devnull, shell=True)
        tiller_pod_status = proc.stdout.read().rstrip().decode()
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(1) 
    print('  - sleeping to allow tiller to warm-up')
    time.sleep(3)


def start_command_for_provisioner(provisioner_name, dns_domain_name):
    """
    generate a command to start/converge a cluster

    """
    print('Using provisioner: ' + provisioner_name)
    if provisioner_name in THIRD_PARTY_TOOL_OPTIONS:
        start_cmd_template = THIRD_PARTY_TOOL_OPTIONS[provisioner_name]['init_cmd_template']
    else:
        sys.exit("provisioner must be minikube or terraform")

    if provisioner_name == "minikube":
        start_cmd = start_cmd_template.format(dns_domain_name, "xhyve")
    elif provisioner_name == "terraform":
        start_cmd = start_cmd_template.format(dns_domain_name)
    return start_cmd

