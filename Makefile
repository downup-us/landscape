# Acts on a single Landscape namespace at a time (smallest unit to CRUD is namespace)
# Helm charts can be deployed independently of Landscaper using helm install / helm upgrade utils
#
# Deploy environment
#  deploys to current branch to context in `kubectl config current-context`
#
# TODO: use https://github.com/shaneramey/vault-backup for backup/restore
#
#
# Usage:
#  make PROVISIONER=[ minikube | terraform ] [GCE_PROJECT=myproj-123456] deploy
SHELL := /bin/bash

PROVISIONER := minikube

GIT_BRANCH := $(shell git symbolic-ref HEAD 2>/dev/null | cut -d"/" -f 3)

# required for Terraform GCE deployments
GCE_PROJECT_ID := ""

# override these settings on command-line for operations on a single namespace
K8S_NAMESPACE := "__all_namespaces__"
HELM_CHART_INSTALL := "__all_charts__"

# default command to deploy the cluster.
# intention is to append to this command, based on the provisioner
DEPLOY_CMD := landscape deploy --provisioner=$(PROVISIONER) --namespace=$(K8S_NAMESPACE) --chart=$(HELM_CHART_INSTALL)

# Jenkinsfile stages, plus other targets
.PHONY: deploy

deploy:
ifeq ($(PROVISIONER),terraform)
	${DEPLOY_CMD} --gce-project-id=$(GCE_PROJECT_ID) 
else
	${DEPLOY_CMD}
endif
