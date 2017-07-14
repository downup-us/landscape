#! /usr/bin/env python3

"""
landscape: deploy Helm charts

Provisions Kubernetes clusters and Helm charts, with secrets in Hashicorp Vault

Usage:
  landscape deploy      [--provisioner=<provisioner>] [--gce-project-id=<gce_project_id>] [--cluster-dns-domain=<dns_domain>] [--landscaper-git-branch=<git_branch>] [--namespace=<namespace>] [--chart=<chart>]
  landscape environment [--list-targets] [--fetch-lastpass] [--landscaper-git-branch=<git_branch>]
  landscape test
  landscape verify
  landscape report
  landscape purge
  landscape csr

Options:
  --provisioner=<provisioner>             k8s provisioner [default: minikube].
  --gce-project-id=<gce_project_id>       in GCE environment, which project ID to use
  --cluster-dns-domain=<dns_domain>       DNS domain used for inside-cluster DNS defaults to $GIT_BRANCH.local.
  --landscaper-git-branch=<git_branch>    Helm / Landscaper charts branch to deploy (dev vs. master, etc.) [default: master].
  --namespace=<namespace>                 install only charts under specified namespace
  --chart=<chart>                         Install only chart name
  --list-targets                          show available deployment targets
  --fetch-lastpass                        Fetches values from Lastpass and puts them in Vault
Provisioner can be one of minikube, terraform.
"""

import docopt
import os
import sys
import subprocess
import platform

from . import THIRD_PARTY_TOOL_OPTIONS
from .local import populate_vault_with_lastpass_secrets
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

    arg_deploy                = args.get('deploy')
    arg_environment           = args.get('environment')
    k8s_provisioner           = args.get('--provisioner')
    gce_project_id            = args.get('--gce-project-id')
    dns_domain                = args.get('--cluster-dns-domain')
    landscaper_branch         = args.get('--landscaper-git-branch')
    namespace                 = args.get('--namespace')
    chart                     = args.get('--charts')
    list_targets              = args.get('--list-targets')
    fetch_lastpass            = args.get('--fetch-lastpass')

    os_type = platform.system() # e.g. 'Darwin'

    # Cluster DNS domain inside containers' /etc/resolv.conf
    if not dns_domain:
        dns_domain = landscaper_branch + '.local'
        # GKE requires 'cluster.local' as DNS domain
        if k8s_provisioner == 'terraform':
            dns_domain = 'cluster.local'
            print("Forcing domain to {0} in GKE (terraform)".format(dns_domain))

    k8s_context = get_k8s_context_for_provisioner(k8s_provisioner,
                                                    gce_project_id,
                                                    landscaper_branch)
    # All deployment information is stored in Vault

    if arg_deploy:
        # deploy cluster and initialize Helm's tiller pod
        deploy_cluster(provisioner=k8s_provisioner,
                        project_id=gce_project_id,
                        git_branch=landscaper_branch,
                        dns_domain=dns_domain)
        wide_open_security() # workaround until RBAC ClusterRoles are in place
        deploy_helm_charts(k8s_provisioner, landscaper_branch)
        # local tool setup
    elif arg_environment:
        if list_targets:
            target_provisioner = target_provisioner
            target_list = list_deploy_target_clusters(target_provisioner)
            for t in target_list:
              print(t)
        if fetch_lastpass:
            target_provisioner = target_provisioner
            landscaper_branch = landscaper_branch
            populate_vault_with_lastpass_secrets(landscaper_branch)
            for t in target_list:
              print(t)
        else:
            setup_environment(os_type, k8s_provisioner)


if __name__ == "__main__":
    main()


