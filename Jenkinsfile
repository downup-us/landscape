#! /usr/bin/env groovy

properties([parameters([choice(choices: getTargets(), description: 'Kubernetes Provisioner', name: 'PROVISIONER')])])

def getVaultCacert() {
    return "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
}

def getTargets() {
// gets provisioner targets from Vault
// returns a list used for dynamic Jenkinsfile parameters
    vaultEnvVars = [
        "VAULT_ADDR=https://http.vault.svc.master.local:8200",
        "VAULT_CACERT=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt",
        "VAULT_TOKEN=111ff8ae-2bb1-70e4-35ab-51e5856538ee"
    ]
    def sout = new StringBuilder(), serr = new StringBuilder()
    minikube_targets_cmd = "ls"
    minikube_targets = minikube_targets_cmd.execute(vaultEnvVars, new File("/"))
    minikube_targets.consumeProcessOutput(sout, serr)
    minikube_targets.waitForOrKill(5000)
    println(sout)
    println(serr)
    return sout
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

