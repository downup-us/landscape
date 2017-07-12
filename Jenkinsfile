#! /usr/bin/env groovy

import com.cwctravel.hudson.plugins.extended_choice_parameter.ExtendedChoiceParameterDefinition

def git_branch     = "${env.BRANCH_NAME}"
def cluster_domain = "${env.BRANCH_NAME}.local"

def possible_provisioner_targets="landscape environment --list-targets".execute().text

def getVaultAddress() {
    domain = "grep search /etc/resolv.conf | awk '{ print \$NF }'".execute().text
    return "https://http.vault.svc." + domain + ":8200"
}

def getVaultCacert() {
    return "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
}

def getTargets() {
    return sh(script: 'landscape environment --list-targets --target-provisioner=minikube', returnStdout: true).trim()
}

def workspaceName() {
    return "myworkspace"
}
def vault_addr = getVaultAddress()
def vault_cacert = getVaultCacert()
def k8s_targets = getTargets()

timestamps {
    properties([
       parameters([
          choice(choices: "x\ny\nz\n", description: 'Please select an environment', name: 'Env')
       ])
    ])

    node('landscape') {
        ws(workspaceName()) {
            try {
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
                    withCredentials([[$class: 'UsernamePasswordMultiBinding',
                                      credentialsId: 'vault',
                                      usernameVariable: 'VAULT_USER',
                                      passwordVariable: 'VAULT_PASSWORD']]) {
                        sh "vault auth -method=ldap username=$VAULT_USER password=$VAULT_PASSWORD 2>&1 > /dev/null && export VAULT_TOKEN=\$(vault read -field id auth/token/lookup-self) && export PATH=$PATH:/usr/local/bin && make GIT_BRANCH=${env.BRANCH_NAME} PROVISIONER=${params.PROVISIONER} deploy"
                    }
                }
                stage('Verify') {
                    sh "echo make GIT_BRANCH=${env.BRANCH_NAME} PROVISIONER=${params.PROVISIONER} verify"
                    sh "make GIT_BRANCH=${env.BRANCH_NAME} PROVISIONER=${params.PROVISIONER} verify"
                }
                stage('Report') {
                    sh "echo make GIT_BRANCH=${env.BRANCH_NAME} PROVISIONER=${params.PROVISIONER} report"
                    sh "make GIT_BRANCH=${env.BRANCH_NAME} PROVISIONER=${params.PROVISIONER} report"
                }
            } catch (exc) {
                echo 'Something failed, I should sound the klaxons!'
                throw exc
            }
        }
    }
}