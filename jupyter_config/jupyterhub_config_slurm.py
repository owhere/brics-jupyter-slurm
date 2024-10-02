import os
import logging
import sys

from dummyauthenticator import DummyAuthenticator

# Set the authenticator class to DummyAuthenticator for testing
c.JupyterHub.authenticator_class = DummyAuthenticator
c.Authenticator.admin_users = {'admin'}
c.Authenticator.allowed_users = {'admin'}
c.LocalAuthenticator.create_system_users = True

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Log the final authenticator setup
logger.info("Using NoPasswordPAMAuthenticator for passwordless access")
logger.info("Assigned NoPasswordPAMAuthenticator")

# URL config
c.ConfigurableHTTPProxy.api_url = 'http://0.0.0.0:8018'
c.JupyterHub.bind_url = 'http://:38024'
c.JupyterHub.hub_connect_ip = '0.0.0.0'
c.JupyterHub.base_url = '/'

# Spawner settings
import sys
sys.path.append('/usr/local/bin/') 
from brics_slurm_spawner import BricsSlurmSpawner

spawner = BricsSlurmSpawner()
spawner.user = type('User', (object,), {'name': 'admin'})() 
logger.info(f'spawner user user user set up: {spawner.user}')

c.JupyterHub.spawner_class = BricsSlurmSpawner

# Configure the spawner's environment and notebook settings
c.BricsSlurmSpawner.cmd = ['jupyter-lab']
c.BricsSlurmSpawner.args = ['--notebook-dir=/tmp/admin/notebooks', '--ip=0.0.0.0', '--allow-root']
c.BricsSlurmSpawner.debug = True
c.BricsSlurmSpawner.default_url = '/lab'
c.BricsSlurmSpawner.ip = '0.0.0.0'
c.BricsSlurmSpawner.notebook_dir = '/tmp/admin/notebooks'
c.BricsSlurmSpawner.start_timeout = 300  
c.BricsSlurmSpawner.http_timeout = 300  
c.BricsSlurmSpawner.job_status = ['R']   # Specify the status that indicates running ('R' for Slurm)

# Slurm settings
c.BricsSlurmSpawner.batch_query_cmd = 'squeue -j {job_id}'  # Query job status
c.BricsSlurmSpawner.batch_cancel_cmd = 'scancel {job_id}'   # Cancel job


c.Spawner.default_url = '/lab'
c.Spawner.notebook_dir = '~/notebooks'

c.JupyterHub.log_level = 'DEBUG'
c.JUpyterHub.log_file = '/srv/jupyterhub/jupyterhub.log'
