"""
Commands to run operate configuration of a user's workstation
"""

import sys
import subprocess

def start_local_dev_vault():
    """
    Starts a local Hashicorp Vault container used to hold bootstrap secrets

    TODO: have it return the dev-vault's VAULT_TOKEN
    """
    docker_running_cmd = 'docker ps'
    docker_stopped = subprocess.call(docker_running_cmd, shell=True)
    if docker_stopped:
        sys.exit('Docker daemon not running - exiting.')
    check_dev_vault_cmd = 'docker ps | grep dev-vault'
    need_dev_vault = subprocess.call(check_dev_vault_cmd, shell=True)
    if need_dev_vault:
        start_dev_vault_cmd = THIRD_PARTY_TOOL_OPTIONS['minikube']['dev_vault_init_cmd']
        print("Starting dev-vault with command: {0}".format(start_dev_vault_cmd))
        subprocess.call(start_dev_vault_cmd, shell=True)

def populate_vault_with_lastpass_secrets(vault_branch_subtree):
    lastpass_secrets = THIRD_PARTY_TOOL_OPTIONS['lastpass']['folder']
    populate_cmd = "lpass show {0}/master --notes".format(lastpass_secrets)
    sys.exit("run this command to populate Vault: {0}".format(populate_cmd))
    #subprocess.call(populate_cmd, shell=True)

