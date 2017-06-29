#! /usr/bin/env bash

# Deploys a Landscaper environment from namespaces/ subdir of repo

# Requires:
#  - this script run from within a git repo, so that GIT_BRANCH can be detected
#  - `kubectl config get-contexts` to have the desired context selected
#  - Vault authentication done before running this script (VAULT_TOKEN set)

set -u

GIT_BRANCH=$1
NAMESPACE_ARG=$2

# Where secrets are loaded in lastpass
LASTPASS_FOLDER="Shared-k8s/k8s-landscaper"

# each branch has its own set of deployments
echo "Using GIT_BRANCH ${GIT_BRANCH}"

darwin=false; # MacOSX compatibility
case "`uname`" in
    Darwin*) export sed_cmd=`which gsed` ;;
    *) export sed_cmd=`which sed` ;;
esac

function join_by {
    local IFS="$1"; shift; echo "$*";
}

function tell_to_populate_secrets {
    MISSING_SECRET_LIST=("$@")
    echo MISSING_SECRET_LIST $MISSING_SECRET_LIST
}

function generate_envconsul_config {
    GIT_BRANCH=$1
    K8S_NAMESPACE=$2
    CHART_NAME=$3

    # Envconsul Vault setup
    if [ ! -x $sed_cmd ]; then
        echo "ERROR: sed command $sed_cmd not found " \
            " (MacOS users: run brew install gnu-sed)"
        exit 2
    fi
    if [ ! -f /usr/local/bin/envconsul ]; then
        echo "envconsul not installed. aborting"
        exit 2
    fi

    V_PREFIX="/secret/landscape/$GIT_BRANCH/$K8S_NAMESPACE/$CHART_NAME"
    echo "    - Using Vault prefix $V_PREFIX"
    echo "    - Writing envconsul-config.hcl (.gitignored)"

    # generate envconsul template
    # are we using TLS or not?
    VAULT_SSL_ENABLED="false"
    if [[ $VAULT_ADDR == https* ]]; then
        VAULT_SSL_ENABLED="true"
    fi
    if [ -z ${VAULT_CACERT+x} ]; then
        VAULT_CACERT=""
    fi
    VAULT_TOKEN=$(vault read -field id auth/token/lookup-self)

    cp -f envconsul-config.hcl.tmpl envconsul-config.hcl
    envconsul_vars=(
        GIT_BRANCH
        VAULT_ADDR
        VAULT_CACERT
        VAULT_SSL_ENABLED
        VAULT_TOKEN
        K8S_NAMESPACE
        CHART_NAME
    )
    for envconsul_var in ${envconsul_vars[@]}; do
        tag=__${envconsul_var}__ # e.g, __GIT_BRANCH__
        envvar=${!envconsul_var}
        $sed_cmd -i "s^${tag}^${envvar}^g" envconsul-config.hcl
    done
}

function vault_to_env {
    GIT_BRANCH=$1
    CHART_NAME=$2
    K8S_NAMESPACE=$3

    # Generate envconsul config
    generate_envconsul_config $GIT_BRANCH $K8S_NAMESPACE $CHART_NAME
    # Read secrets from Vault
    ENVCONSUL_COMMAND="envconsul -config=./envconsul-config.hcl -secret="$V_PREFIX" -once -retry=1s -pristine -upcase env"

    echo "Running ${ENVCONSUL_COMMAND}"
    for envvar_kv in `$ENVCONSUL_COMMAND`; do
        envvar_k=`echo $envvar_kv | awk -F= '{ print $1}'`
        echo "  - setting secret $envvar_k"
        export $envvar_kv
    done
}

function apply_namespace {
    K8S_NAMESPACE=$1

    missing_secret_list=() # in case any secrets are missing
    chart_errors=() # report any errors

    CURRENT_CONTEXT=`kubectl config get-contexts | grep '^\*' | awk '{ print $2 }'`

    # Apply landscape
    LANDSCAPER_COMMAND="landscaper apply -v --context=$CURRENT_CONTEXT --namespace=$K8S_NAMESPACE namespaces/$K8S_NAMESPACE/*.yaml"
    echo
    echo "Running \`$LANDSCAPER_COMMAND\`"
    LANDSCAPER_OUTPUT=`$LANDSCAPER_COMMAND 2>&1`
    echo "$LANDSCAPER_OUTPUT"

    # Landscaper error if secrets are missing (set upstream in landscaper repo)
    LANDSCAPER_SECRET_ERROR='Secret\ not\ found\ in\ environment'
    while read -r line ; do
        MISSING_SECRET=`echo $line | awk '{ print $NF }' \
                        | cut -d= -f2 | tr '-' '_'`
        missing_secret_list+=("$MISSING_SECRET=${MISSING_SECRET}_value")
    done < <(echo "$LANDSCAPER_OUTPUT" | grep "$LANDSCAPER_SECRET_ERROR")

    # Print error if one exists
    while read -r line; do
        chart_errors+=("$line")
    done < <(echo "$LANDSCAPER_OUTPUT" | grep -i error)

    if [[ ${#missing_secret_list[@]} -ge 1 ]]; then
        echo
        echo '### WARNING WARNING WARNING'
        echo " Secrets are missing. Setting them with the below commands will"
        echo "  wipe out any existing secrets. Be sure that's what you want"

        missing_secret_count=${#missing_secret_list[@]}
        echo
        echo Vault is missing $missing_secret_count secrets.
        echo
        echo NOTE: If you have lastpass-cli installed, run:
        echo
        echo "lpass show $LASTPASS_FOLDER/$GIT_BRANCH --notes"
        echo
        echo First read existing secrets, and see if you want to replace them
        echo
        echo vault read $V_PREFIX
        echo vault delete $V_PREFIX
        echo vault write $V_PREFIX \\
        for unset_secret in "${missing_secret_list[@]:0:missing_secret_count-1}"; do
            echo " " $unset_secret "\\"
        done
        echo " " ${missing_secret_list[missing_secret_count-1]}
        echo
        echo '### WARNING WARNING WARNING'
        echo
        exit 3
    fi

    if [[ ${#chart_errors[@]} -ge 1 ]]; then
        for chart_error in "${chart_errors[@]}"; do
            echo $chart_error
        done
        exit 2
    fi
    helm status ${K8S_NAMESPACE}-${CHART_NAME}
}

if [ "${NAMESPACE_ARG}" == "__all_namespaces__" ]; then
	# Loop through namespace
    for NAMESPACE_W_DIR in namespaces/*; do
        if [ -d $NAMESPACE_W_DIR ]; then
            NAMESPACE=`echo $NAMESPACE_W_DIR | awk -F/ '{ print $2 }'`
            echo "###"
            echo "# Namespace: $NAMESPACE"
            echo "###"
            echo
            echo "Checking status of namespace $NAMESPACE"
            kubectl get ns $NAMESPACE > /dev/null
            if [ $? -eq 0 ]; then
                echo "    - Namespace $NAMESPACE already exists"
            else
                echo -n "    - Namespace $NAMESPACE doesn't exist. Creating..."
                kubectl create ns $NAMESPACE
                echo " done."
            fi
            echo
            for CHART_YAML in namespaces/${NAMESPACE}/*.yaml; do
                CHART_NAME=`cat $CHART_YAML | grep '^name: ' | awk -F': ' '{ print $2 }'`
                echo "Chart $CHART_NAME: exporting Vault secrets for git branch $GIT_BRANCH in namespace $NAMESPACE to env vars"
                vault_to_env $GIT_BRANCH $CHART_NAME $NAMESPACE
            done
            # run landscaper
            apply_namespace $NAMESPACE
        fi
    done
else
    if [ -d "namespaces/${NAMESPACE_ARG}" ]; then
        echo "###"
        echo "# Namespace: ${NAMESPACE_ARG}"
        echo "###"
        echo
        echo "Checking status of namespace ${NAMESPACE_ARG}"
        kubectl get ns ${NAMESPACE_ARG} > /dev/null
        if [ $? -eq 0 ]; then
            echo "    - Namespace ${NAMESPACE_ARG} already exists"
        else
            echo -n "    - Namespace ${NAMESPACE_ARG} doesn't exist. Creating..."
            kubectl create ns ${NAMESPACE_ARG}
            echo " done."
        fi
        echo
        for CHART_YAML in namespaces/${NAMESPACE_ARG}/*.yaml; do
        	CHART_NAME=`cat $CHART_YAML | grep '^name: ' | awk -F': ' '{ print $2 }'`
            echo "Chart $CHART_NAME: exporting Vault secrets to env vars"
            vault_to_env $GIT_BRANCH $CHART_NAME ${NAMESPACE_ARG}
        done
        # run landscaper
        apply_namespace ${NAMESPACE_ARG}
    fi
fi
