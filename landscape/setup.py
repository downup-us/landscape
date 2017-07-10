"""
Sets up the local machine tools
"""

import subprocess
import sys

from . import THIRD_PARTY_TOOL_OPTIONS

def install_prerequisites(os_type):
	for external_program in THIRD_PARTY_TOOL_OPTIONS:
		program_version = THIRD_PARTY_TOOL_OPTIONS[external_program]['version']

		print(" - installing: {0} version: {1}".format(external_program,
														program_version))
		install_program(external_program, program_version, os_type)

def install_program(program_name, program_version, os_platform):
	INSTALL_TEMPLATES = {
		'lastpass': {
			'Darwin': 'which lpass > /dev/null || (brew update && ' + \
						'brew install lastpass-cli --with-pinentry)',
			'Linux': 'which lpass > /dev/null || apt-get update && apt-get install openssl libcurl4-openssl-dev libxml2 libssl-dev libxml2-dev pinentry-curses xclip cmake build-essential pkg-config'
		},
		'vault': {
			'Darwin': 'which vault > /dev/null || (curl -LO ' + \
						'https://releases.hashicorp.com/vault/' + \
						'{version}/' + \
						'vault_{version}_{platform}_amd64.zip && ' + \
						'unzip -d /usr/local/bin/ ' + \
						'vault_{version}_{platform}_amd64.zip && ' + \
						'rm vault_{version}_{platform}_amd64.zip)',
			'Linux': 'which vault > /dev/null || (curl -LO ' + \
						'https://releases.hashicorp.com/vault/' + \
						'{version}/' + \
						'vault_{version}_{platform}_amd64.zip && ' + \
						'unzip -d /usr/local/bin/ ' + \
						'vault_{version}_{platform}_amd64.zip && ' + \
						'rm vault_{version}_{platform}_amd64.zip)',
		},
		'kubectl': {
			'Darwin': 'which kubectl > /dev/null || (curl -LO ' + \
						'https://storage.googleapis.com/kubernetes-release/' + \
						'release/v{version}/bin/{platform}/amd64/' + \
						'kubectl && chmod +x kubectl && ' + \
						'mv kubectl /usr/local/bin/)',
			'Linux': 'which kubectl > /dev/null || (curl -LO ' + \
						'https://storage.googleapis.com/kubernetes-release/' + \
						'release/v{version}/bin/{platform}/amd64/' + \
						'kubectl && chmod +x kubectl && ' + \
						'mv kubectl /usr/local/bin/)'
		},
		'helm': {
			'Darwin': 'which helm > /dev/null || (curl -LO ' + \
						'https://storage.googleapis.com/kubernetes-helm/' + \
						'helm-v{version}-{platform}-amd64.tar.gz && ' + \
						'tar zxvf helm-v{version}-{platform}-amd64.tar.gz ' + \
						'--strip-components=1 {platform}-amd64/helm && ' + \
						'chmod +x helm && ' + \
						'mv helm /usr/local/bin/ && ' + \
						'rm helm-v{version}-{platform}-amd64.tar.gz)',
			'Linux': 'which helm > /dev/null || (curl -LO ' + \
						'https://storage.googleapis.com/kubernetes-helm/' + \
						'helm-v{version}-{platform}-amd64.tar.gz && ' + \
						'tar zxvf helm-v{version}-{platform}-amd64.tar.gz ' + \
						'--strip-components=1 {platform}-amd64/helm && ' + \
						'chmod +x helm && ' + \
						'mv helm /usr/local/bin/ && ' + \
						'rm helm-v{version}-{platform}-amd64.tar.gz)'
		},
		'landscaper': {
			'Darwin': 'which landscaper > /dev/null || (curl -LO ' + \
						'https://github.com/Eneco/landscaper/releases/' + \
						'download/{version}/' + \
						'landscaper-{version}-{platform}-amd64.tar.gz && ' + \
						'tar zxvf ' + \
						'landscaper-{version}-{platform}-amd64.tar.gz ' + \
						'landscaper && mv landscaper /usr/local/bin/ && ' + \
						'rm landscaper-{version}-{platform}-amd64.tar.gz)',
			'Linux': 'which landscaper > /dev/null || (curl -LO ' + \
						'https://github.com/Eneco/landscaper/releases/' + \
						'download/{version}/' + \
						'landscaper-{version}-{platform}-amd64.tar.gz && ' + \
						'tar zxvf ' + \
						'landscaper-{version}-{platform}-amd64.tar.gz ' + \
						'landscaper && mv landscaper /usr/local/bin/ && ' + \
						'rm landscaper-{version}-{platform}-amd64.tar.gz)'
		},
		'terraform': {
			'Darwin': 'which terraform > /dev/null || (curl -LO ' + \
						'https://releases.hashicorp.com/terraform/' + \
						'{version}/' + \
						'terraform_{version}_{platform}_amd64.zip && ' + \
						'unzip -d /usr/local/bin ' + \
						'terraform_{version}_{platform}_amd64.zip && ' + \
						'rm terraform_{version}_{platform}_amd64.zip)',
			'Linux': 'which terraform > /dev/null || (curl -LO ' + \
						'https://releases.hashicorp.com/terraform/' + \
						'{version}/' + \
						'terraform_{version}_{platform}_amd64.zip && ' + \
						'unzip -d /usr/local/bin ' + \
						'terraform_{version}_{platform}_amd64.zip && ' + \
						'rm terraform_{version}_{platform}_amd64.zip)'
		},
		'minikube': {
			'Darwin': 'which minikube > /dev/null || (curl -Lo minikube ' + \
						'https://storage.googleapis.com/minikube/' + \
						'releases/v{version}/minikube-{platform}-amd64 && ' + \
						'chmod +x minikube-{platform}-amd64 && ' + \
						'mv minikube-{platform}-amd64 /usr/local/bin/minikube)',
			'Linux': 'which minikube > /dev/null || (curl -Lo minikube ' + \
						'https://storage.googleapis.com/minikube/' + \
						'releases/v{version}/minikube-{platform}-amd64 && ' + \
						'chmod +x minikube-{platform}-amd64 && ' + \
						'mv minikube-{platform}-amd64 /usr/local/bin/minikube)'
		},

	}

	# install the tools listed in INSTALL_TEMPLATES
	install_cmd_template = INSTALL_TEMPLATES[program_name][os_platform]
	# translate detected OS name to package filename
	platform_id = os_platform.lower()
	install_cmd = install_cmd_template.format(version=program_version,
												platform=platform_id)
	print("   - running {0}".format(install_cmd))
	command_failed = subprocess.call(install_cmd, shell=True)
	if command_failed:
		sys.exit("install third-party-tool {0} " + \
					"failed. Ran {1}".format(program_name, install_cmd))
	