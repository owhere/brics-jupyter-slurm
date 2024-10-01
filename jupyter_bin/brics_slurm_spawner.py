import logging
from batchspawner import SlurmSpawner

class BricsSlurmSpawner(SlurmSpawner):
    def user_env(self, env):
        """
        Set user environment variables
        
        These are used in spawner submitting environment (see :func:`BatchSpawnerBase.submit_batch_script`) and the 
        user session job environment (see :func:`BatchSpawnerBase._req_keepvars_default`).

        This overrides :func:`UserEnvMixin.user_env`, avoiding accessing the Unix password database using
        :func:`pwd.getpwnam` (this does not make sense when running inside a container).

        :return: environment dictionary with USER, HOME, and SHELL keys set
        """
        self.log.debug("Entering BricsSlurmSpawner.user_env()")
        env["USER"] = self.req_username
        env["HOME"] = self.req_homedir
        env["SHELL"] = "/bin/bash"
        return env
    
    def get_batch_script(self):
        script_content = f"""#!/bin/bash
            #SBATCH --job-name=test_job
            #SBATCH --output=result.out

            echo "Running a test job at "
            date
            sleep 60
            date
            """ 
        return script_content

    async def submit_batch_script(self):
        script_content = self.get_batch_script() 

        # Submit the job using sbatch directly
        out = await self.run_command(
            f'sbatch --parsable', 
            input=script_content, 
            env=self.get_env()
        )

        return out.strip()  # Return the job ID or relevant information
