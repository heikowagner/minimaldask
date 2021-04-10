from dask.distributed import Client
import dask.array as da
import subprocess
import re
from kubernetes_helper import start_dask_cluster, delete_dask_cluster

# We determine the ip of the master node using kubectl
p = subprocess.Popen("kubectl cluster-info", stdout=subprocess.PIPE)
kube_conf = p.stdout.read().decode()
master_ip = re.findall(r"//([\s\S]*?):", kube_conf, re.MULTILINE)[0]


def main():
    start_dask_cluster()
    dask_client = Client(master_ip + ":30086") # noqa

    x = da.random.random((10000, 10000), chunks=(1000, 1000))
    y = x + x.T
    z = y[::2, 5000:].mean(axis=1)

    print(z.compute())
    delete_dask_cluster(namespace="default")


if __name__ == "__main__":
    main()
