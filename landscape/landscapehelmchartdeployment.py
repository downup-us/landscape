"""Landscape class to handle deployments of clusters and Landscaper configs."""



class LandscapeHelmChartDeployment(object):
    """Deploys Kubernetes Helm charts (but not clusters)

    Arguments:
        provision(provisioner obj): k8s provisioner (minikube, terraform, etc)
        config(provisionerConfig obj): provisioner-specific options

    Methods:
        new(
            provisioner=minikube,
            gce_project_id=develop-123456,
            landscaper-branch=master
            ):
        an object representing a Landscape set of Helm charts.

        deploy():
            Converge helm chart set towards its desired-state
    """
    
    def __init__(self):
        print("LandscapeHelmCharts placeholder")
