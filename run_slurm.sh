#! /bin/bash
set -euo pipefail

ENGINE_CMD=${CONTAINER_ENGINE_CMD:-docker}
BIND_IP=${CONTAINER_BIND_IP:-}

set -o xtrace

podman run --rm --name jupyter-slurm \
    --privileged \
    -p ${BIND_IP}${BIND_IP:+:}38024:38024 \
    --user root \
    --mount type=bind,source=$PWD/slurm_logs,target=/srv/slurm_logs \
    --mount type=bind,source=$PWD/slurm_config/slurm.conf,target=/etc/slurm/slurm.conf \
    --mount type=bind,source=$PWD/slurm_spool/slurmd,target=/var/spool/slurmd \
    --mount type=bind,source=$PWD/slurm_spool/slurmctld,target=/var/spool/slurmctld \
    --mount type=bind,source=$PWD/jupyter_config,target=/srv/jupyterhub \
    --mount type=bind,source=$PWD/jupyter_notebooks,target=/tmp/admin/notebooks \
    --mount type=bind,source=$PWD/jupyter_bin/brics_slurm_spawner.py,target=/opt/brics_jupyter/brics_slurm_spawner.py \
    --mount type=bind,source=$PWD/jupyter_bin/brics_token_authenticator.py,target=/opt/brics_jupyter/brics_token_authenticator.py \
    brics-jupyter-slurm:latest \
    jupyterhub -f /srv/jupyterhub/jupyterhub_config_slurm.py 

#   sleep infinity (for debugging)

set +o xtrace
