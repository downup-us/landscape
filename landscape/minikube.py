import subprocess

def apply_minikube_cluster(dns_domain):
    """
    creates or converges a minikube-provisioned cluster to its desired-state

    Arguments:
     - provisioner: minikube or terraform
     - dns_domain: dns domain to use for cluster

    Returns: None
    """
    minikube_status_cmd = THIRD_PARTY_TOOL_OPTIONS['minikube']['minikube_status_cmd']
    proc = subprocess.Popen(minikube_status_cmd, stdout=subprocess.PIPE, shell=True)
    minikube_status = proc.stdout.read().rstrip().decode()

    if not minikube_status == 'Running':
        start_minikube(provisioner, dns_domain)
    else:
        print('  - minikube cluster previously provisioned. Re-using ')
    minikube_disable_addons()
    hack_wide_open_security() # FIXME: create ClusterRoles


def start_minikube(provisioner, dns_domain):
    """
    Starts minikube. Prints an error if non-zero exit status
    """
    k8s_provision_command = start_command_for_provisioner(provisioner, dns_domain)
    print('  - running ' + k8s_provision_command)
    minikube_failed = subprocess.call(k8s_provision_command, shell=True)
    if minikube_failed:
        sys.exit('ERROR: minikube failure')

def minikube_disable_addons():
    """
    Disable default add-ons for minikube that we are replacing with helm deploys
    """
    disable_addons_cmd = THIRD_PARTY_TOOL_OPTIONS['minikube']['minikube_addons_disable_cmd']
    print('- disabling unused minikube addons ' + disable_addons_cmd)
    print('  - running ' + disable_addons_cmd)
    failed_to_disable_addons = subprocess.call(disable_addons_cmd, shell=True)
    if failed_to_disable_addons:
        print('ERROR: failed to disable addons')

