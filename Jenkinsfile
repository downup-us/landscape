#! /usr/bin/env groovy

withContext(mycontext) {
    properties([parameters([choice(choices: "a\nb\n", description: 'Kubernetes Provisioner', name: 'PROVISIONER')])])
}

def getVaultCacert() {
    return "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
}

def getTargets() {
    minikube_targets = sh(filePath: '/tmp', script: 'landscape environment --list-targets --target-provisioner=minikube', returnStdout: true).trim()
    return minikube_targets
}

node('landscape') {
    mycontext = getContext(hudson.FilePath)
    println(mycontext)


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

