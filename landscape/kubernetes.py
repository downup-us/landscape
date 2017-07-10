import subprocess
import sys
import os
import hvac

def kubernetes_get_context():
    get_context_cmd = "kubectl config current-context"
    print(' - running ' + get_context_cmd)
    proc = subprocess.Popen(get_context_cmd, stdout=subprocess.PIPE, shell=True)
    k8s_context = proc.stdout.read().rstrip().decode()
    return k8s_context


def kubernetes_set_context(context):
    set_context_cmd = "kubectl config use-context {0}".format(context)
    print(' - running ' + set_context_cmd)
    set_context_failed = subprocess.call(set_context_cmd, shell=True)
    if set_context_failed:
    	sys.exit('Error setting context. Exiting')

def kubernetes_apply_credentials(context):
    """
    Pulls credentials from Vault and applies them to local user

    Arguments:
        context to get credentials for
        ex: gke_staging-123456_us-west1-a_master

    Returns: None
    """
    if 'VAULT_TOKEN' not in os.environ:
        sys.exit("VAULT_TOKEN needed. Please set that in your environment")

    secret_item = "/secret/terraform/{0}/auth".format(project_id)
    print('        - reading Vault subtree: ' + secret_item)

    vault_client = hvac.Client(token=os.environ['VAULT_TOKEN'])
    vault_chart_secrets_item = vault_client.read(secret_item)

    # compare landscaper secrets with vault contents
    # exit with list of secrets set in landscaper yaml but not in vault
    if not vault_chart_secrets_item:
        print("          - no chart secrets in vault")
    else:   
        vault_chart_secrets = vault_chart_secrets_item['data']