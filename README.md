# brics-jupyter-slurm
This repo runs JupyterHub in a docker, which installs Slurm and JupyterHub. The goal is to be able to test any customisation of JupyterHub, e.g. run it with Slurm. 

## Design principles

**Have all customisation outside of container. Use different configuration files to adjust Slurm and JupyterHub for different settings.**

- **use different authenticator and spawner by using different JupyterHub config files.**
- **mount all folders and files when run the container.**

## Design

### 1. Base image 

Start with a working Slurm docker as a base image, such as [Docker-Slurm](https://github.com/owhere/docker-slurm).

### 2. Set up folders and files for Slurm 

Configure the Slurm as needed, to have followings folders and files outside of the container.

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

### 3. Set up folders and files for JupyterHub

Install JupyterHub dependencies in the docker but have following folders and files outside of the container.

```plaintext
├── jupyter_bin/         
│   └── brics_slurm_spawner    
│   └── brics_token_anthenticator    
├── jupyter_config/                
│   ├── jupyterhub_config.py         
│   └── jupyterhub_config_slurm.py
└── jupyter_notebooks (Optional)
```

### 4. Run container with folders and files mounted.

Use [Run Script](run.sh)

### 5. Run Slurm inside the container and monitor the jobs if using Slurm Spawner.

```
slurmctld
slurmd
sinfo
```

## Try out

### 0. Prerequisites

Docker is required to use for the container. 

Podman is also tested in MacOS, after setting up podman with following alias.

```shell
alias docker=podman
```

### 1. Build the docker

```shell
$git clone https://github.com/owhere/brics-jupyter-slurm.git 
$cd brics-jupyter-slurm
$docker build -t brics-jupyter-slurm .
```

### 2. Run JupyterHub without Slurm
This script is to run a jupyterhub with DummyAuthenticator and SimpleLocalProcessSpawner.

```shell
$bash run.sh
$ssh -L 38024:localhost:38024 your_user@remote_host
```

Then you can access JupyterHub on http://127.0.0.1:38024 and login with user admin and no password needed.

### 3. Run JupyterHub with Slurm
This script is to run a jupyterhub with BricsAuthenticator and BricsSlurmSpawner.

#### Start run in a shell or VS Code Terminal
```shell
$bash run_slurm.sh
$ssh -L 38024:localhost:38024 your_user@remote_host
```

#### Use another shell to access the container to start slurm
```shell
$docker exec -it jupyter-slurm bash
$slurmctld
$slurmd  
$sinfo
PARTITION AVAIL  TIMELIMIT  NODES  STATE NODELIST
debug*       up   infinite      1    mix localhost
```
Please check files in slurm_log and slurm_spool to make sure everything works.

#### Access JupyterHub

Then you can access JupyterHub on http://127.0.0.1:38024 and login with user admin and no password needed.

At this point, please check the queue, you should see something like
```shell
$squeue
JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
    33     debug spawner-    admin  R      18:02      1 localhost
```

Please then check the slurm log at /home/admin/ inside container
```shell
$tail -f /home/admin/jupyterhub_slurmspawner_33.log
```

### Diagnosis

1. When container starts, you can check if it is running as expected like following:

```shell
$docker ps 
CONTAINER ID   IMAGE                        COMMAND                  CREATED        STATUS        PORTS              NAMES
c1de9a675fe4   brics-jupyter-slurm:latest   "jupyterhub -f /srv/…"   2 hours ago   Up 2 hours   <ports-exposed>   jupyter-slurm
```
Make sure the port-exposed are expected.

2. Check docker logs
```shell
$docker logs -f jupyter-slurm
```

3. To stop the docker gracefully and clean it up, use:
```shell
$docker stop jupyter-slurm
$docker rm jupyter-slurm
```

4. To clean up the jobs in the queue forcefully, inside the container, use
```shell
$scancel -f <job-id>
```

5. Resume the node, if in drain or down state, inside the container, use
```shell
$scontrol update NodeName=localhost State=RESUME Reason="Manual clear of drain state"
```

6. Remove all untracked data files from bind-mounted directories (e.g. `slurm_spool/`)

   ```shell
   # Dry-run to see what would be deleted
   git clean -x -d --dry-run

   # Delete untracked files
   git clean -x -d --force
   ```
