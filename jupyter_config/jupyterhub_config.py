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


# Log the final authenticator setup
logger.info("Assigned NoPasswordPAMAuthenticator")

# URL config
c.ConfigurableHTTPProxy.api_url = 'http://127.0.0.1:8018'
c.JupyterHub.bind_url = 'http://0.0.0.0:38024'
c.JupyterHub.hub_connect_ip = '0.0.0.0'
c.JupyterHub.base_url = '/'

# Spawner settings
c.JupyterHub.spawner_class = 'jupyterhub.spawner.SimpleLocalProcessSpawner'
c.Spawner.cmd = ['jupyter-lab']
c.Spawner.args = ['--notebook-dir=/tmp/admin/notebooks', '--ip=0.0.0.0', '--allow-root']
c.Spawner.debug = True
c.Spawner.default_url = '/lab'
c.Spawner.ip = '0.0.0.0'
c.Spawner.notebook_dir = '/tmp/admin/notebooks'

c.JupyterHub.log_level = 'DEBUG'
c.JUpyterHub.log_file = '/srv/jupyterhub/jupyterhub.log'