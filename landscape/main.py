#! /usr/bin/env python3

"""landscape: deploy Helm charts

Usage:
  landscape deploy [--provisioner=<provisioner>] [--gce-project-id=<gce_project_name>] [--landscaper-branch=<git_branch>] [--cluster-domain=<domain>]
  landscape environment [--list-targets] [--target-provisioner=<provisioner>]
  landscape test
  landscape verify
  landscape report
  landscape purge
  landscape csr

Options:
  --provisioner=<provisioner>             k8s provisioner [default: minikube].
  --cluster-domain=<domain>               domain used for inside-cluster DNS (defaults to ${GIT_BRANCH}.local)
  --gce-project-id=<gce_project_name>     in GCE environment, which project ID to use
  --namespace=<namespace>                 deploy charts in specified namespace
  --all-namespaces                        deploy charts in all namespaces
  --list-targets                          show available deployment targets
  --landscaper-branch=<git_branch>        Helm / Landscaper charts branch to deploy (dev vs. master, etc.) [default: master].
  --target-provisioner=<provisioner>      List targets only for specific deploy provisioner [default: __all_deploy_targets__].

Provisioner can be one of minikube, terraform.
"""

import docopt
import os
import sys
import subprocess
import platform

from . import THIRD_PARTY_TOOL_OPTIONS
from .setup import install_prerequisites
from .environment import setup_environment
from .cluster import deploy_cluster
from .landscaper import deploy_helm_charts
from .utils import (get_k8s_context_for_provisioner, gce_get_zone_for_project_and_branch_deployment, list_deploy_target_clusters, eprint)
from .kubernetes import kubectl_use_context
from .hack import wide_open_security

from . import verify
from . import report
from . import purge
from . import csr


def main():
    # branch is used to pull secrets from Vault, and to distinguish clusters
    args = docopt.docopt(__doc__)
    
    os_type = platform.system() # e.g. 'Darwin'

    # Which kubernetes provisioner to use.
    k8s_provisioner  = args['--provisioner']
    
    # Project name to deploy. Must be in Vault
    gce_project_name = args['--gce-project-id']

    # which branch to deploy (used for Vault key lookup)
    git_branch_name = args['--landscaper-branch']

    # not useful for gke deployments; it's always cluster.local there
    cluster_domain   = args['--cluster-domain']

    # Cluster DNS domain inside containers' /etc/resolv.conf
    if not cluster_domain:
        cluster_domain = git_branch_name + '.local'
        # GKE requires 'cluster.local' as DNS domain
        if k8s_provisioner == 'terraform':
            cluster_domain = 'cluster.local'
    
    k8s_context = get_k8s_context_for_provisioner(k8s_provisioner,
                                                    gce_project_name,
                                                    git_branch_name)
    # All deployment information is stored in Vault

    if args['deploy']:
        # deploy cluster and initialize Helm's tiller pod
        deploy_cluster(provisioner=k8s_provisioner, project_id=gce_project_name, git_branch=git_branch_name, dns_domain=cluster_domain)
        wide_open_security() # workaround until RBAC ClusterRoles are in place
        deploy_helm_charts(k8s_provisioner, git_branch_name)
    # local tool setup
    elif args['environment']:
        if args['--list-targets']:
            target_provisioner = args['--target-provisioner']
            list_deploy_target_clusters(target_provisioner)
        else:
            setup_environment(os_type, k8s_provisioner)
if __name__ == "__main__":
    main()


