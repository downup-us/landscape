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
    print("project_id={0}".format(project_id))
    credentials_cmd = 'terraform output get-credentials-command'
    dns_check_succeeds = test_dns_domain('terraform', dns_domain)
    if dns_check_succeeds:
        terraform_cmd_tmpl = THIRD_PARTY_TOOL_OPTIONS['terraform']['init_cmd_template']
        terraform_cmd = terraform_cmd_tmpl.format(project_id, git_branch_name)
        print('  - applying terraform state with command: ' + terraform_cmd)
        failed_to_apply_terraform = subprocess.call(terraform_cmd, cwd=template_dir, shell=True)
        if failed_to_apply_terraform:
            sys.exit('ERROR: terraform command failed')
        print('  - obtaining terraform credentials with command: ' + terraform_cmd)
        subprocess.call(credentials_cmd, cwd=template_dir, shell=True)
    else:
        err_msg = "ERROR: DNS validation failed for {}".format(dns_domain)
        sys.exit(err_msg)


