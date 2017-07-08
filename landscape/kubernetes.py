import subprocess
import sys

def kubernetes_get_context():
    get_context_cmd = "kubectl config current-context"
    print(' - running ' + get_context_cmd)
    proc = subprocess.Popen(get_context_cmd, stdout=subprocess.PIPE, shell=True)
    k8s_context = proc.stdout.read().rstrip().decode()
    return k8s_context


def kubernetes_set_context(k8s_context):
    set_context_cmd = "kubectl config use-context {0}".format(k8s_context)
    print(' - running ' + set_context_cmd)
    set_context_failed = subprocess.call(set_context_cmd, shell=True)
    if set_context_failed:
    	sys.exit('Error setting context. Exiting')