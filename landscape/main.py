#! /usr/bin/env python3

"""landscape: deploy Helm charts

Usage:
  landscape deploy [--provisioner=<provisioner] [--cluster-domain=<domain>] [--gce-project-id=<gce_project_name>]
  landscape environment
  landscape test
  landscape verify
  landscape report
  landscape purge
  landscape csr

Options:
  --provisioner=<provisioner>             k8s provisioner [default: minikube].
  --cluster-domain=<domain>               Domain used for inside-cluster DNS (defaults to ${GIT_BRANCH}.local)
  --gce-project-id=<gce_project_name>     In GCE environment, which project ID to use
  --ns=<namespace>                        deploy charts in specified namespace
  --all-namespaces                        deploy charts in all namespaces

Provisioner can be one of minikube, terraform.
"""

import docopt
import os
import sys
import subprocess

from . import DEFAULT_OPTIONS
from .environment import setup_environment
from .cluster import provision_cluster
from .landscaper import deploy_helm_charts
from .utils import (git_get_branch, get_k8s_context_for_provisioner, gce_get_region_for_project_and_branch_deployment)
from .kubernetes import kubernetes_set_context
# from .vault import gke_get_region_for_project_name
from . import verify
from . import report
from . import purge
from . import csr


def main():
    # terraform
    # a gce deployment is composed of
    #  - project name
    #
    # a gke deployment is composed of:
    #  - branch name
    git_branch_name = git_get_branch()

    args = docopt.docopt(__doc__)
    k8s_provisioner  = args['--provisioner']
    gce_project_name = args['--gce-project-id']
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
    if args['deploy']:
        provision_cluster(provisioner=k8s_provisioner, dns_domain=cluster_domain, project_id=gce_project_name, git_branch=git_branch_name)

        kubernetes_set_context(k8s_context)
        deploy_helm_charts(k8s_provisioner, git_branch_name)
    elif args['environment']:
        setup_environment(k8s_provisioner)

if __name__ == "__main__":
    main()


