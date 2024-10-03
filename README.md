# brics-jupyter-slurm
This repo runs JupyterHub in a docker, which installs Slurm and JupyterHub. The goal is to be able to test any customisation of JupyterHub and can test it with Slurm. 

## design principles

Have all customisation outside of container. Use different configuration files to adjust Slurm and JupyterHub for different settings.

- use different authenticator and spawner by using different JupyterHub config files.
- mount all folders and files when run the container.

1. Star with a working Slurm docker as a base image, such as [Docker-Slurm](https://github.com/owhere/docker-slurm).

2. Configure the Slurm as needed, to have followings folders and files outside of container to control Slurm

```plaintext
├── slurm_config/                     
│   └── slurm.conf           
├── slurm_logs/                  
│   ├── slurmctld.log          
│   └── slurmd.log   
└── slurm_spool/                 
    ├── slurmctld            
    └── slurmd
```                 

3. Install JupyterHub Dependencies in the docker but have following folders and files outside of container.

```plaintext
├── jupyter_bin/         
│   └── brics_slurm_spawner    
│   └── brics_token_anthenticator    
├── jupyter_config/                
│   ├── jupyterhub_config.py         
│   └── jupyterhub_config_slurm.py
└── jupyter_notebooks (Optional)
```

4. Start container with folders and files mounted.

5. Start Slurm inside the container and monitor the jobs if using Slurm Spawner.

## Try out

0. Prerequisites

Docker is required to use for the container. Podman is also possible, but not tested yet.

Prepare a user (i.e. admin) in your host, to mimic the container set up.
```shell
    useradd -m admin && \
    echo "admin:$6$LCWPfNvA26GTyP5p$cPpAXROBc9eOOaGRUYTrKrj1ELd5/DQy6.QtvKbzrCgeEce1Dlw2R4IZvxSvd08WGdghKQC1AKcv82wcMiHXx/" | chpasswd && \
    echo "admin ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
```
This user should be the owner to run JupyterHub and Slurm Service

```
    sudo chown -R admin:admin jupter_config 
    sudo chown -R admin:admin jupter_notebooks
    sudo chown -R admin:admin slurm_config
    sudo chown -R admin:admin slurm_logs 
    sudo chown -R admin:admin slurm_spool
    sudo -u admin
```

1. Build the docker

```shell
cd brics-jupyter-slurm
docker build -t brics_slurm_jupyter .
```

2. Run JupyterHub without Slurm
This script is to run a jupyterhub with DummyAuthenticator and SimpleLocalProcessSpawner.

```shell
bash run.sh
ssh -L 38024:localhost:38024 -L 8888:localhost:8888 your_user@remote_host
```

Then you can access JupyterHub on http://127.0.0.1:38024 and login with user admin and no password needed.

After login, please check the terminal for the log file, to find something like:

```
To access the server, open this file in a browser:
        file:///tmp/admin/.local/share/jupyter/runtime/jpserver-17-open.html
    Or copy and paste one of these URLs:
        http://1b23c2e48b3c:8888/lab?token=483505f29ccb8373cdb0982a9b96b40b7f286b3bf42cd305
        http://127.0.0.1:8888/lab?token=483505f29ccb8373cdb0982a9b96b40b7f286b3bf42cd305
```
Access the notebook as the URL: http://127.0.0.1:8888/lab?token=483505f29ccb8373cdb0982a9b96b40b7f286b3bf42cd305 

3. Run JupyterHub with Slurm
This script is to run a jupyterhub with BricsAuthenticator and BricsSlurmSpawner.

```shell
bash run_slurm.sh
ssh -L 38024:localhost:38024 -L 8888:localhost:8888 your_user@remote_host
```

Use another shell to access the container to start slurm
```shell
docker exec -it slurm-jupyter bash
slurmctld
slurmd  
sinfo
```

You should have output like
```shell
sinfo
PARTITION AVAIL  TIMELIMIT  NODES  STATE NODELIST
debug*       up   infinite      1    mix localhost
```
If anything issues, please check files in slurm_log and slurm_spool.

Then you can access JupyterHub on http://127.0.0.1:38024 and login with user admin and no password needed.

At this point, please check the queue, you should see something like
```
squeue
JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
    33     debug spawner-    admin  R      18:02      1 localhost
```

Please then check the slurm log at /home/admin/ inside container
```
tail -f /home/admin/jupyterhub_slurmspawner_33.log
```

In the log, you should see following information.
To access the server, open this file in a browser:
        file:///tmp/admin/.local/share/jupyter/runtime/jpserver-17-open.html
    Or copy and paste one of these URLs:
        http://1b23c2e48b3c:8888/lab?token=483505f29ccb8373cdb0982a9b96b40b7f286b3bf42cd305
        http://127.0.0.1:8888/lab?token=483505f29ccb8373cdb0982a9b96b40b7f286b3bf42cd305
```
Access the notebook as the URL: http://127.0.0.1:8888/lab?token=483505f29ccb8373cdb0982a9b96b40b7f286b3bf42cd305 


(TO DO: JupyterHub redirecting JupyterNotebook is not working at the moment, so need to access it from a different browser tab, tested in Firefox)
