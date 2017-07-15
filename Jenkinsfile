#! /usr/bin/env groovy

properties([parameters([choice(choices: getTargets(), description: 'Kubernetes Provisioner', name: 'PROVISIONER')])])

def getVaultCacert() {
    return "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
}

def getTargets() {
    vaultVars = ["VAULT_ADDR=https://http.vault.svc.master.local:8200", "VAULT_CACERT=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt", "VAULT_TOKEN=a0018691-711e-7aeb-69a2-e28878aea0ed"]
    minikube_targets = 'echo -e "a\nb\n"'.execute(vaultVars, new File("/usr/local/bin")).text
    println(minikube_targets)
    return minikube_targets
}

node('landscape') {

    stage('Checkout') {
      checkout scm
    }
    stage('Environment') {
        echo "using git branch: ${git_branch}"
        echo "using clusterDomain: ${git_branch}.local"
        sh "git checkout ${git_branch}"
        sh "make GIT_BRANCH=${env.BRANCH_NAME} PROVISIONER=${params.PROVISIONER} environment"
    }
    stage('Test') {
        sh "echo make GIT_BRANCH=${env.BRANCH_NAME} PROVISIONER=${params.PROVISIONER} test"
        sh "make GIT_BRANCH=${env.BRANCH_NAME} PROVISIONER=${params.PROVISIONER} test"
    }
    stage('Deploy') {
        sh "vault auth -method=ldap username=$VAULT_USER password=$VAULT_PASSWORD 2>&1 > /dev/null && export VAULT_TOKEN=\$(vault read -field id auth/token/lookup-self) && export PATH=$PATH:/usr/local/bin && make GIT_BRANCH=${env.BRANCH_NAME} PROVISIONER=${params.PROVISIONER} deploy"
    }
    stage('Verify') {
        sh "echo make GIT_BRANCH=${env.BRANCH_NAME} PROVISIONER=${params.PROVISIONER} verify"
        sh "make GIT_BRANCH=${env.BRANCH_NAME} PROVISIONER=${params.PROVISIONER} verify"
    }
    stage('Report') {
        sh "echo make GIT_BRANCH=${env.BRANCH_NAME} PROVISIONER=${params.PROVISIONER} report"
        sh "make GIT_BRANCH=${env.BRANCH_NAME} PROVISIONER=${params.PROVISIONER} report"
    }
}

