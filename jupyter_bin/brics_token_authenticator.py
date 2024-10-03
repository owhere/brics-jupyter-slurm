from jupyterhub.auth import Authenticator
from tornado import gen

class BricsAuthenticator(Authenticator):
    async def authenticate(self, handler, data):
        """
        Authenticate the user by returning the username directly, 
        similar to DummyAuthenticator.
        """
        # Extract username from the provided form data
        username = data.get("username", None)
        
        # In this case, we just return the username like DummyAuthenticator.
        if username:
            # Custom logic here
            return username
        else:
            return None
