import subprocess

def wide_open_security():
    """
    Temporary work-around until ClusterRole RBAC is implemented
    """
    need_crb = subprocess.call('kubectl get clusterrolebinding ' + \
                                'permissive-binding', shell=True)
    hack_cmd = 'kubectl create clusterrolebinding ' + \
                                    'permissive-binding ' + \
                                    '--clusterrole=cluster-admin ' + \
                                    '--user=admin ' + \
                                    '--user=kubelet ' + \
                                    '--group=system:serviceaccounts'
    if need_crb:
        print('  - creating permissive clusterrolebinding')
        print('    - running ' + hack_cmd)
        subprocess.call(hack_cmd, shell=True)
    else:
        print('  - permissive clusterrolebinding already exists ' + hack_cmd)


