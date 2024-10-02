import logging
import re
from batchspawner import SlurmSpawner

class BricsSlurmSpawner(SlurmSpawner):
    """
    Custom SlurmSpawner for the Brics project with tailored environment variables
    and a custom batch script for job submission.
    """
    
    def user_env(self, env):
        """
        Customizes the user environment variables before starting the job.
        """
        self.log.debug("Entering BricsSlurmSpawner.user_env()")
        # Set custom environment variables for the user
        env["USER"] = self.user.name  # req_username in batchspawner is self.user.name
        env["HOME"] = f'/home/{self.user.name}'  # Set a custom home directory path
        env["SHELL"] = "/bin/bash"  # Set the shell to bash
        return env
