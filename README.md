# minimaldask
A dask kubernetes deployment including a small dask image form arm64, amd64 and arm/v7. Suitable to run at an local Raspberry Pi Cluster as well as GCloud or similar.

[![Docker Build/Publish Image](https://github.com/heikowagner/minimaldask/actions/workflows/main.yml/badge.svg)](https://github.com/heikowagner/minimaldask/actions/workflows/main.yml)

## Quickstart

- Connect to your cluster using kubectl (https://kubernetes.io/docs/tasks/access-application-cluster/access-cluster/)
- Clone this repo `git clone https://github.com/heikowagner/minimaldask.git`
- Install the python package -> Go to repo folder and run `pip install .`
- Run dasky.py
