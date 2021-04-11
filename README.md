# minimaldask
[![Docker Build/Publish Image](https://github.com/heikowagner/minimaldask/actions/workflows/main.yml/badge.svg)](https://github.com/heikowagner/minimaldask/actions/workflows/main.yml)

This dask kubernetes deployment includes a small dask image form arm64, amd64 and arm/v7. Suitable to run at an local Raspberry Pi Cluster as well as GCloud or similar.
Get your Dask Cluster up and runnning in seconds, carry out a computation send from your local Python send and executed by the cluster. For more informations about the project, check my website: https://www.thebigdatablog.com/building-a-minimal-cost-efficient-dask-cluster/

## Quickstart

- Connect to your cluster using kubectl (https://kubernetes.io/docs/tasks/access-application-cluster/access-cluster/)
- Clone this repo `git clone https://github.com/heikowagner/minimaldask.git`
- Install the python package -> Go to repo folder and run `pip install .`
- Run dasky.py
