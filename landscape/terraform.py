import subprocess
import sys
from .utils import test_dns_domain
from . import THIRD_PARTY_TOOL_OPTIONS

def apply_terraform_cluster(dns_domain, project_id, template_dir, git_branch_name):
    """
    creates or converges a terraform-provisioned cluster to its desired-state

    Arguments:
     - dns_domain: dns domain to use for cluster
                   In GKE environment, must be cluster.local
    Returns: post-execute command for terraform credentials init
    """
    dns_check_succeeds = test_dns_domain('terraform', dns_domain)
    if dns_check_succeeds:
        terraform_cmd_tmpl = THIRD_PARTY_TOOL_OPTIONS['terraform']['init_cmd_template']
        terraform_cmd = terraform_cmd_tmpl.format(project_id, git_branch_name)
        print('  - applying terraform state with command: ' + terraform_cmd)
        failed_to_apply_terraform = subprocess.call(terraform_cmd, cwd=template_dir, shell=True)
        if failed_to_apply_terraform:
            sys.exit('ERROR: terraform command failed')
        get_gke_credentials(template_dir)
    else:
        err_msg = "ERROR: DNS validation failed for {}".format(dns_domain)
        sys.exit(err_msg)


def get_gke_credentials(tf_template_dir):
    """
    Pull GKE kubernetes credentials from GCE and writes to ~/.kube/config

    Returns: None, but gke credentials should be in ~/.kube/config
    """
    credentials_cmd = 'terraform output get-credentials-command'
    print('  - obtaining terraform script with command: ' + credentials_cmd)
    proc = subprocess.Popen(credentials_cmd, cwd=tf_template_dir, stdout=subprocess.PIPE, shell=True)
    get_credentials_command = proc.stdout.read().rstrip().decode()
    print('  - getting credentials with command: ' + get_credentials_command)
    failed_to_set_creds = subprocess.call(get_credentials_command, cwd=tf_template_dir, shell=True)
    if failed_to_set_creds:
        sys.exit('ERROR: failed to obtain credentials and/or set them')
