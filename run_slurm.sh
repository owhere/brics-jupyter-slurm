#! /bin/bash
set -euo pipefail

# To use an alternative container engine command, specify as first argument, e.g.
#   run.sh podman
# Default with no argument is to use docker
if (( $# == 0 )); then
  ENGINE_CMD="docker"
elif (( $# == 1 )); then
  ENGINE_CMD="$1"
else
  echo "Error: Incorrect number of arguments"
  echo "Usage: $0 [container engine command]"
  exit 1
fi

set -o xtrace

${ENGINE_CMD} run --name jupyter-slurm \
    --privileged \
    -p 6817:6817 -p 6818:6818 \
    -p 38024:38024   \
    -p 8888:8888 \
    --user root \
    --mount type=bind,source=$PWD/slurm_logs,target=/srv/slurm_logs \
    --mount type=bind,source=$PWD/slurm_config/slurm.conf,target=/etc/slurm/slurm.conf \
    --mount type=bind,source=$PWD/slurm_spool/slurmd,target=/var/spool/slurmd \
    --mount type=bind,source=$PWD/slurm_spool/slurmctld,target=/var/spool/slurmctld \
    --mount type=bind,source=$PWD/jupyter_config,target=/srv/jupyterhub \
    --mount type=bind,source=$PWD/jupyter_notebooks,target=/tmp/admin/notebooks \
    --mount type=bind,source=$PWD/jupyter_bin/brics_slurm_spawner.py,target=/usr/local/bin/brics_slurm_spawner.py \
    --mount type=bind,source=$PWD/jupyter_bin/brics_token_authenticator.py,target=/usr/local/bin/brics_token_authenticator.py \
    brics-jupyter-slurm:latest \
    jupyterhub -f /srv/jupyterhub/jupyterhub_config_slurm.py 

#   sleep infinity (for debugging)

set +o xtrace