#! /usr/bin/env groovy

def getVaultCacert() {
    return "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
}

def getTargets() {
// gets provisioner targets from Vault
// returns a list used for dynamic Jenkinsfile parameters
    vaultEnvVars = [
        "VAULT_ADDR=https://http.vault.svc.master.local:8200",
        "VAULT_CACERT=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt",
        "VAULT_TOKEN=e3bd1ca1-0b7d-fa00-a91c-e4e41aa419d8"
    ]
    minikube_targets_cmd = "/usr/local/bin/landscape environment --list-targets"
    def sout = new StringBuilder(), serr = new StringBuilder()
    target_list = minikube_targets_cmd.execute(vaultEnvVars, new File("/"))
    target_list.consumeProcessOutput(sout, serr)
    target_list.waitForOrKill(5000)
    if(target_list != 0) {
        println("Return value non-zero")
        println(sout, serr)
        System.exit(1)
    }
    println("landscape command succeeded ")
    println(sout, serr)
    return sout
}

properties([parameters([choice(choices: getTargets(), description: 'Kubernetes Provisioner', name: 'PROVISIONER')])])


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

