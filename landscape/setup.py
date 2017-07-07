"""
Sets up the local machine tools
"""

import subprocess
import sys

from . import THIRD_PARTY_TOOL_OPTIONS

def install_prerequisites(os_type):
	for external_program in THIRD_PARTY_TOOL_OPTIONS:
		program_version = THIRD_PARTY_TOOL_OPTIONS[external_program]['version']
		print("P: {0} V: {1}".format(external_program, program_version))
		install_program(external_program, program_version, os_type)

def install_program(program_name, program_version, os_platform):
	INSTALL_TEMPLATES = {
		'lastpass': {
			'Darwin': 'which lpass || brew update && brew install lastpass-cli --with-pinentry'
		},
		'vault': {
			'Darwin': 'which vault || (curl -LO ' + \
						'https://releases.hashicorp.com/vault/' + \
						'{version}/' + \
						'vault_{version}_{platform}_amd64.zip && ' + \
						'unzip -d /usr/local/bin/ ' + \
						'vault_{version}_{platform}_amd64.zip && ' + \
						'rm vault_{version}_{platform}_amd64.zip)'
		},
		'kubectl': {
			'Darwin': 'which kubectl || (curl -LO ' + \
						'https://storage.googleapis.com/kubernetes-release/' + \
						'release/v{version}/bin/{platform}/amd64/' + \
						'kubectl && chmod +x kubectl && ' + \
						'mv kubectl /usr/local/bin/)'
		},
		'helm': {
			'Darwin': 'which helm || (curl -LO ' + \
						'https://storage.googleapis.com/kubernetes-helm/' + \
						'helm-v{version}-{platform}-amd64.tar.gz && ' + \
						'chmod +x helm && ' + \
						'mv helm /usr/local/bin/ && ' + \
						'rm helm-v{version}-{platform}-amd64.tar.gz)'
		},
		'landscaper': {
			'Darwin': 'which landscaper || (curl -LO ' + \
						'https://github.com/Eneco/landscaper/releases/' + \
						'download/{version}/' + \
						'landscaper-{version}-{platform}-amd64.tar.gz)'
		},
		'terraform': {
			'Darwin': 'which terraform || (curl -LO ' + \
						'https://releases.hashicorp.com/terraform/' + \
						'{version}/' + \
						'terraform_{version}_{platform}_amd64.zip)'
		},

	}

	# install the tools listed in INSTALL_TEMPLATES
	for thirdpartytool in INSTALL_TEMPLATES:
		install_cmd_template = INSTALL_TEMPLATES[thirdpartytool][os_platform]
		# translate detected OS name to package filename
		platform_id = os_platform.lower()
		install_cmd = install_cmd_template.format(version=program_version,
													platform=platform_id)
		print("install_cmd={0}".format(install_cmd))
		command_failed = subprocess.call(install_cmd, shell=True)
		if command_failed:
			sys.exit("install third-party-tool {0} " + \
						"failed. Ran {1}".format(thirdpartytool, install_cmd))
	