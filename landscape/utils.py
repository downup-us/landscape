# -*- coding: utf-8 -*-
"""Various helper utilities"""

import subprocess
import re
import hvac
import os
import sys

def namespace_exists(namespace):
    if subprocess.call(['kubectl', 'get', 'ns', namespace], shell=True):
        return True
    else:
        return False
	

def git_get_branch():
	return subprocess.check_output(['git', 'symbolic-ref', 'HEAD', '--short' ]).rstrip().decode()


def test_dns_domain(k8s_provisioner, cluster_dns_domain):
    """
    Validate DNS domain.
    GKE-only supports cluster.local for now, so enforce that

    Returns:
        True if domain validates
        False if domain validation fails
    """
    if k8s_provisioner == 'terraform' and cluster_dns_domain != 'cluster.local':
        return False
    if valid_cluster_domain(cluster_dns_domain):
        return True

def valid_cluster_domain(domain):
    """
    Returns True if DNS domain validates
    """
    return re.match('[a-z]{1,63}\.local', domain)

def gce_get_region_for_project_and_branch_deployment(gce_project, git_branch):
  """
  Returns a region based on the gce_project + git_branch of a GCE deployment
  """
  return 'us-west1-a'


def get_k8s_context_for_provisioner(provisioner, project_name, git_branch_name):
    if provisioner == 'terraform':
      git_branch_name = 'master'
      region = gce_get_region_for_project_and_branch_deployment(project_name, git_branch_name)
      return "gke_{0}_{1}_{2}".format(project_name, region, git_branch_name)
    else:
      # covers minikube
      return provisioner

def list_deploy_targets():
    vault_client = hvac.Client(token=os.environ['VAULT_TOKEN'])

    terraform_targets_root = '/secret/terraform/'
    terraform_targets_in_vault = vault_client.list(terraform_targets_root)
    available_terraform_targets = terraform_targets_in_vault['data']['keys']
    for target_with_trailing_slash in available_terraform_targets:
        target = re.sub('\/$', '', target_with_trailing_slash)
        print(target)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
