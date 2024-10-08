import os
import logging
import sys
import batchspawner

sys.path.append('/usr/local/bin/') 
from brics_slurm_spawner import BricsSlurmSpawner
from brics_token_authenticator import BricsAuthenticator

# Set the authenticator
c.JupyterHub.authenticator_class = BricsAuthenticator
c.Authenticator.admin_users = {'admin'}
c.Authenticator.allowed_users = {'admin'}
c.LocalAuthenticator.create_system_users = True

# URL config
c.ConfigurableHTTPProxy.api_url = 'http://0.0.0.0:8018'
c.JupyterHub.bind_url = 'http://:38024'
c.JupyterHub.hub_connect_ip = '0.0.0.0'
c.JupyterHub.base_url = '/'

# Spawner settings
spawner = BricsSlurmSpawner()
spawner.user = type('User', (object,), {'name': 'admin'})() 
c.JupyterHub.spawner_class = BricsSlurmSpawner

# Configure the spawner's environment and notebook settings
#c.BricsSlurmSpawner.cmd = ['jupyter-lab']
c.BricsSlurmSpawner.args = ['--notebook-dir=/tmp/admin/notebooks', '--ip=0.0.0.0', '--allow-root']
c.BricsSlurmSpawner.debug = True
c.BricsSlurmSpawner.default_url = '/lab'
c.BricsSlurmSpawner.ip = '0.0.0.0'
c.BricsSlurmSpawner.notebook_dir = '/tmp/admin/notebooks'
c.BricsSlurmSpawner.start_timeout = 300  
c.BricsSlurmSpawner.http_timeout = 300  
c.BricsSlurmSpawner.poll_interval = 10  # Set polling interval to 10 seconds


# Slurm settings
c.BricsSlurmSpawner.batch_query_cmd = 'squeue -j {job_id}'  # Query job status
c.BricsSlurmSpawner.batch_cancel_cmd = 'scancel {job_id}'   # Cancel job

c.JupyterHub.log_level = logging.DEBUG