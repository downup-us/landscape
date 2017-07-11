#! /usr/bin/env groovy

def git_branch     = "${env.BRANCH_NAME}"
def cluster_domain = "${env.BRANCH_NAME}.local"

def possible_provisioner_targets="landscape environment --list-targets".execute().text

def getTargets() {
    withCredentials([[$class: 'UsernamePasswordMultiBinding',
                      credentialsId: 'vault',
                      usernameVariable: 'VAULT_USER',
                      passwordVariable: 'VAULT_PASSWORD']]) {
        "vault auth -method=ldap username=$VAULT_USER password=$VAULT_PASSWORD 2>&1 > /dev/null && export VAULT_TOKEN=\$(vault read -field id auth/token/lookup-self) && landscape environment --list-targets".execute().text
    }
}

def getClusterDomain() {
    return "grep search /etc/resolv.conf | awk '{ print $NF }'".execute().text
}

pipeline {
    agent any

    environment {
        VAULT_ADDR     = "https://http.vault.svc." + getClusterDomain() + ":8200"
        VAULT_CACERT   = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
    }

    options {
        timeout(time: 1, unit: 'HOURS') 
    }

    parameters {
        booleanParam(name: 'DEBUG_BUILD', defaultValue: true, description: 'turn on debugging')
        choice(name: 'PROVISIONER', choices: getTargets(), description: 'cluster provisioner')
    }

    triggers {
        pollSCM('* * * * *')
    }

    stages {
        stage('Environment') {
            steps {
                echo "using git branch: ${env.BRANCH_NAME}"
                echo "using clusterDomain: ${env.BRANCH_NAME}.local"
                sh "git checkout ${git_branch}"
                sh "make GIT_BRANCH=${env.BRANCH_NAME} PROVISIONER=${params.PROVISIONER} environment"
            }
        }
        stage('Test') {
            steps {
                sh "echo make GIT_BRANCH=${env.BRANCH_NAME} PROVISIONER=${params.PROVISIONER} test"
                sh "make GIT_BRANCH=${env.BRANCH_NAME} PROVISIONER=${params.PROVISIONER} test"
            }
        }
        stage('Deploy') {
            steps {
                withCredentials([[$class: 'UsernamePasswordMultiBinding',
                                  credentialsId: 'vault',
                                  usernameVariable: 'VAULT_USER',
                                  passwordVariable: 'VAULT_PASSWORD']]) {
                    sh "vault auth -method=ldap username=$VAULT_USER password=$VAULT_PASSWORD 2>&1 > /dev/null && export VAULT_TOKEN=\$(vault read -field id auth/token/lookup-self) && export PATH=$PATH:/usr/local/bin && make GIT_BRANCH=${env.BRANCH_NAME} PROVISIONER=${params.PROVISIONER} deploy"
                }
            }
        }
        stage('Verify') {
            steps {
                sh "echo make GIT_BRANCH=${env.BRANCH_NAME} PROVISIONER=${params.PROVISIONER} verify"
                sh "make GIT_BRANCH=${env.BRANCH_NAME} PROVISIONER=${params.PROVISIONER} verify"
            }
        }
        stage('Report') {
            steps {
                sh "echo make GIT_BRANCH=${env.BRANCH_NAME} PROVISIONER=${params.PROVISIONER} report"
                sh "make GIT_BRANCH=${env.BRANCH_NAME} PROVISIONER=${params.PROVISIONER} report"
            }
        }
    }
}
