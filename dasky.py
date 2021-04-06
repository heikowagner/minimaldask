from kubernetes import client, config, watch
from dask.distributed import Client, progress
from os import path
import yaml
import dask.array as da
import time
import logging
import json
import subprocess
import re

# We determine the ip of the master node using kubectl
p = subprocess.Popen("kubectl cluster-info", stdout=subprocess.PIPE)
kube_conf=p.stdout.read().decode()
master_ip= re.findall(r"//([\s\S]*?):", kube_conf, re.MULTILINE)[0]

config.load_kube_config()
k8s_apps_v1 = client.AppsV1Api()
k8s_core_v1 = client.CoreV1Api()

def start_dask_cluster(namespace="default", worker_replicas=5, pip_packages=None, apt_packages=None):
    with open(path.dirname(__file__) + "/service.yaml") as f:
        dep = yaml.safe_load(f)
        try:
            k8s_core_v1.delete_namespaced_service("master-node", namespace=namespace)
        except:
            pass
        resp = k8s_core_v1.create_namespaced_service(body=dep, namespace=namespace)
        print(resp)

    with open(path.dirname(__file__) + "/sheduler.yaml") as f:
        resp = update_or_deploy(f, pip_packages=pip_packages, apt_packages=apt_packages)
    with open(path.dirname(__file__) + "/worker.yaml") as f:
        resp = update_or_deploy(f, replicas = worker_replicas, pip_packages=pip_packages, apt_packages=apt_packages)

def delete_dask_cluster(namespace):
    k8s_core_v1.delete_namespaced_service("master-node", namespace=namespace)
    k8s_apps_v1.delete_namespaced_deployment("sheduler", namespace=namespace)
    k8s_apps_v1.delete_namespaced_deployment("worker", namespace=namespace)
    logging.info("dask cluster deleted")

def update_or_deploy(file, namespace="default", replicas = 1, pip_packages=None, apt_packages=None):
    dep = yaml.safe_load(file)
    logging.debug(dep)
    dep["spec"]["replicas"] = replicas
    #put packages here
    name = dep["metadata"]["name"]
    try:
        resp = k8s_apps_v1.read_namespaced_deployment(name, namespace=namespace)
        logging.info("Deployment already present. status='%s'" % resp.metadata.name)
        resp = k8s_apps_v1.replace_namespaced_deployment(name=name, namespace=namespace, body=dep)
        logging.info("Deployment updated. status='%s'" % resp.metadata.name)
    except client.exceptions.ApiException as e:
        if e.reason=="Not Found":
            resp = k8s_apps_v1.create_namespaced_deployment(
                body=dep, namespace=namespace)
            logging.info("Deployment created. status='%s'" % resp.metadata.name)
        else:
            raise client.exceptions.ApiException(e)

    while True:
        resp = k8s_apps_v1.read_namespaced_deployment(name=name,
                                                namespace='default')
        if resp.status.ready_replicas == replicas:
            break
        time.sleep(1)
        logging.info("pending...")
    logging.info("Done.")
    return resp

def main():
    start_dask_cluster()
    dask_client = Client(master_ip+':30086')

    x = da.random.random((10000, 10000), chunks=(1000, 1000))
    y = x + x.T
    z = y[::2, 5000:].mean(axis=1)

    print( z.compute() )
    delete_dask_cluster(namespace="default")

if __name__ == '__main__':
    main()

