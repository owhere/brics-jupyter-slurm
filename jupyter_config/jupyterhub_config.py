# Set the authenticator class to DummyAuthenticator for testing
c.JupyterHub.authenticator_class = 'dummy'
c.Authenticator.admin_users = {'admin'}
c.Authenticator.allowed_users = {'admin'}

# URL config
c.ConfigurableHTTPProxy.api_url = 'http://0.0.0.0:8018'
c.JupyterHub.bind_url = 'http://:38024'
c.JupyterHub.hub_connect_ip = '0.0.0.0'
c.JupyterHub.base_url = '/'

# Spawner settings
c.JupyterHub.spawner_class = 'simple'
c.Spawner.args = []
c.Spawner.debug = True
c.Spawner.default_url = '/lab'
c.Spawner.ip = '0.0.0.0'
c.Spawner.notebook_dir = '/tmp/admin/notebooks'
c.Spawner.start_timeout = 120
c.Spawner.http_timeout = 120

# Logging
c.JupyterHub.log_level = 'DEBUG'
c.JupyterHub.extra_log_file = '/srv/jupyterhub/jupyterhub.log'
