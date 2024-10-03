#! /bin/bash


docker run --name slurm-jupyter \
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
    brics_slurm_jupyter:latest \
    jupyterhub -f /srv/jupyterhub/jupyterhub_config_slurm.py 
    
#   sleep infinity (for debugging)