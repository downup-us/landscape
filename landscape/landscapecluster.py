class LandscapeCluster(object):
    """Deploys Kubernetes clusters (but not Helm charts)

    Arguments:
        provision(provisioner obj): k8s provisioner (minikube, terraform, etc)
        config(provisionerConfig obj): provisioner-specific options

    Methods:
        new(
            provisioner=minikube, # or terraform
            gce_project_id=develop-123456, # GCE project ID
            landscaper_branch=master # Landscape chart-set for environment
            ):
            an object representing a Landscape-provisioned cluster
        deploy():
            Converge cluster towards its desired-state
    """
    
    def __init__(self, provisioner, gce_project_id, landscaper_branch):
        self.provisioner = provisioner
        self.gce_project_id = gce_project_id
        self.landscaper_branch = landscaper_branch
        print("LandscapeProvisioner placeholder")
