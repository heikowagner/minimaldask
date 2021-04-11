#!/bin/sh

# We start by adding extra apk packages, since pip modules may required library
if [ "$EXTRA_APK_PACKAGES" ]; then
    echo "EXTRA_APK_PACKAGES environment variable found.  Installing."
    apk update
    apk add $EXTRA_APT_PACKAGES
fi

if [ "$EXTRA_PIP_PACKAGES" ]; then
    echo "EXTRA_PIP_PACKAGES environment variable found.  Installing".
    pip install $EXTRA_PIP_PACKAGES
fi


if [ "$WORKER" ]; then
  echo "Worker Node starting"
  dask-worker master-node:$PORT $ARGUMENTS &
else
  echo "Master Node starting"
  dask-scheduler --port $PORT $ARGUMENTS --dashboard &
fi

# Run extra commands
exec "$@"
