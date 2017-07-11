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
    print("   - by convention using landscape branch {0}".format(git_branch))
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


def apply_tiller():
    """
    Checks if Tiller is already installed. If not, install it.
    """
    tiller_pod_status_cmd = THIRD_PARTY_TOOL_OPTIONS['helm']['monitor_tiller_cmd']
    print('Checking tiller status with command: ' + tiller_pod_status_cmd)

    proc = subprocess.Popen(tiller_pod_status_cmd, stdout=subprocess.PIPE, shell=True)
    tiller_pod_status = proc.stdout.read().rstrip().decode()

    # if Tiller isn't initialized, wait for it to come up
    if not tiller_pod_status == "Running":
        print('  - did not detect tiller pod')
        init_tiller(tiller_pod_status_cmd)
    else:
        print('  - detected running tiller pod')

def init_tiller(wait_tiller_ready_cmd):
    helm_provision_command = 'helm init'
    print('  - initializing Tiller with command: ' + helm_provision_command)
    subprocess.call(helm_provision_command, shell=True)
    wait_for_tiller_ready(wait_tiller_ready_cmd)


def wait_for_tiller_ready(monitor_command):
    proc = subprocess.Popen(monitor_command, stdout=subprocess.PIPE, shell=True)
    tiller_pod_status = proc.stdout.read().rstrip().decode()

    print('  - waiting for tiller pod to be ready')
    warm_up_seconds = 5
    while tiller_pod_status != "Running":
        proc = subprocess.Popen(monitor_command, stdout=subprocess.PIPE, shell=True)
        tiller_pod_status = proc.stdout.read().rstrip().decode()
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(1) 
    print("  - sleeping {0} to allow tiller to warm-up".format(warm_up_seconds))
    time.sleep(warm_up_seconds)
