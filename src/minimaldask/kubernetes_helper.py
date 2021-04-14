from kubernetes import client, config
from os import path
import yaml
import time
import logging


config.load_kube_config()
k8s_apps_v1 = client.AppsV1Api()
k8s_core_v1 = client.CoreV1Api()


def start_dask_cluster(
    namespace="default", worker_replicas=5, pip_packages=None, apk_packages=None
):
    with open(path.dirname(__file__) + "/service.yaml") as f:
        dep = yaml.safe_load(f)
        try:
            k8s_core_v1.delete_namespaced_service("master-node", namespace=namespace)
        except:  # noqa
            pass
        resp = k8s_core_v1.create_namespaced_service(body=dep, namespace=namespace)

    add_env=[]
    if pip_packages:
        add_env = add_env + [{'name': 'EXTRA_PIP_PACKAGES', 'value': pip_packages}]
    if apk_packages:
        add_env = add_env + [{'name': 'EXTRA_APK_PACKAGES', 'value': apk_packages}]

    with open(path.dirname(__file__) + "/sheduler.yaml") as f:
        dep = yaml.safe_load(f)
        dep["spec"]["template"]["spec"]["containers"][0]["env"] = dep["spec"]["template"]["spec"]["containers"][0]["env"]+add_env
        resp = update_or_deploy(dep)

    with open(path.dirname(__file__) + "/worker.yaml") as f:
        dep = yaml.safe_load(f)
        dep["spec"]["template"]["spec"]["containers"][0]["env"] = dep["spec"]["template"]["spec"]["containers"][0]["env"]+add_env
        resp = update_or_deploy(dep, replicas=worker_replicas)


def delete_dask_cluster(namespace):
    k8s_core_v1.delete_namespaced_service("master-node", namespace=namespace)
    k8s_apps_v1.delete_namespaced_deployment("sheduler", namespace=namespace)
    k8s_apps_v1.delete_namespaced_deployment("worker", namespace=namespace)
    logging.info("dask cluster deleted")


def update_or_deploy(dep, namespace="default", replicas=1):
    logging.debug(dep)
    dep["spec"]["replicas"] = replicas
    # put packages here
    name = dep["metadata"]["name"]
    try:
        resp = k8s_apps_v1.read_namespaced_deployment(name, namespace=namespace)
        logging.info("Deployment already present. status='%s'" % resp.metadata.name)
        resp = k8s_apps_v1.replace_namespaced_deployment(
            name=name, namespace=namespace, body=dep
        )
        logging.info("Deployment updated. status='%s'" % resp.metadata.name)
    except client.exceptions.ApiException as e:
        if e.reason == "Not Found":
            resp = k8s_apps_v1.create_namespaced_deployment(
                body=dep, namespace=namespace
            )
            logging.info("Deployment created. status='%s'" % resp.metadata.name)
        else:
            raise client.exceptions.ApiException(e)

    while True:
        resp = k8s_apps_v1.read_namespaced_deployment(name=name, namespace="default")
        if resp.status.ready_replicas == replicas:
            break
        time.sleep(1)
        logging.info("pending...")
    logging.info("Done.")
    return resp
