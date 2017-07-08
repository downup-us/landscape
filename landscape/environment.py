###
# Sets up environment (shell, chart repos, other static configuration)
# Used for using landscape CLI tool
###
import subprocess
import os

from . import THIRD_PARTY_TOOL_OPTIONS
from .setup import install_prerequisites

def setup_environment(local_system_os, environment_provisioner):
    """
    Sets environment settings intended to be used across multiple deployments
    Installs local pre-requisites (kubectl, landscaper, helm, etc.)
    Configures helm chart repos. It should also authenticate with vault but that's untested

    Arguments: None

    Returns: None
    """
    install_prerequisites(local_system_os)
    helm_chart_repo_map = THIRD_PARTY_TOOL_OPTIONS['helm']['chart_repos']
    helm_add_chart_repos(helm_chart_repo_map)

    # custom environment per-provisioner type
    if environment_provisioner == 'minikube':
        setup_provisioner_minikube()
    elif environment_provisioner == 'terraform':
        setup_provisioner_terraform()


def setup_provisioner_terraform():
    """
    Initializes user's environment for terraform deployments
    """
    set_gce_credentials(gce_project, gce_region)


def setup_provisioner_minikube():
    """
    Initializes user's environment for minikube deployments
    """
    start_local_dev_vault()


def start_local_dev_vault():
    """
    Starts a local Hashicorp Vault container used to hold bootstrap secrets
    """
    docker_running_cmd = 'docker ps'
    docker_stopped = subprocess.call(docker_running_cmd, shell=True)
    if docker_stopped:
        sys.exit('Docker daemon not running - exiting.')
    check_dev_vault_cmd = 'docker ps | grep dev-vault'
    need_dev_vault = subprocess.call(check_dev_vault_cmd, shell=True)
    if need_dev_vault:
        start_dev_vault_cmd = THIRD_PARTY_TOOL_OPTIONS['minikube']['dev_vault_init_cmd']
        subprocess.call(start_dev_vault_cmd, shell=True)

def get_vault_token(vault_provisioner):
    """
    Auths against local dev-vault and sets VAULT_TOKEN in shell

    Arguments: None

    Returns: Vault auth token pulled from docker's logs
    """
    VAULT_TOKEN_CMD_FOR_ENV = {
        'minikube': "docker logs dev-vault 2>&1 | grep 'Root Token' | ' + \
                        'tail -n 1 | awk '{ print $3 }'",
        'terraform': 'export VAULT_ADDR=https://http.vault.svc.{0} && ' + \
                        'vault auth {1}'
    }

    get_token_cmd = VAULT_TOKEN_CMD_FOR_ENV[vault_provisioner]
    proc = subprocess.Popen(get_token_cmd, stdout=subprocess.PIPE, shell=True)
    vault_auth_token = proc.stdout.read().rstrip().decode()

    return vault_auth_token

def helm_add_chart_repos(repos):
    """
    Adds helm chart repos to current user

    Arguments:
     - repos (dict):
        key: chart repo alias
        value: chart repo url

    Returns: None
    """
    for repo_name in repos:
        repo_url = repos[repo_name]
        print("- Adding Helm Chart Repo {0} at {1}".format(repo_name, repo_url))
        helm_add_chart_repo(repo_name, repo_url)

def helm_add_chart_repo(repo_alias, url):
    """
    Adds a single helm chart repo

    Arguments:
     - repo_alias (string): used to remotely identify/pull helm chart packages
     - url (string): url for chart repo

    Returns: None
    """
    repo_add_cmd = "helm repo add {0} {1}".format(repo_alias, url)
    subprocess.call(repo_add_cmd, shell=True)

def set_gce_credentials(gce_project, gce_region):
    # to load credentials:
    os.environ['GOOGLE_PROJECT'] = gce_project
    os.environ['GOOGLE_REGION'] = gce_region
    os.environ['GOOGLE_CREDENTIALS'] = vault_load_gce_creds()