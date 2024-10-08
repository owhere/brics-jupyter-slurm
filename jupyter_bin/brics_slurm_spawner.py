import logging
import re
from enum import Enum
import asyncio
from traitlets import Unicode
from jinja2 import Template
from batchspawner import SlurmSpawner

def format_template(template, *args, **kwargs):
    """Format a template, either using jinja2 or str.format().

    Use jinja2 if the template is a jinja2.Template, or contains '{{' or
    '{%'.  Otherwise, use str.format() for backwards compatability with
    old scripts (but you can't mix them).
    """
    if isinstance(template, Template):
        return template.render(*args, **kwargs)
    elif "{{" in template or "{%" in template:
        return Template(template).render(*args, **kwargs)
    return template.format(*args, **kwargs)

import re

def parse_job_status(job_output, job_id):
    # Use a regular expression to match the job line with the specified job ID
    for line in job_output.splitlines():
        if line.strip().startswith(str(job_id)):
            parts = re.split(r'\s+', line.strip())
            if len(parts) >= 5:
                return parts[4]  # Assuming the 5th element is the status (ST)
    return None  # Job ID not found

class JobStatus(Enum):
    NOTFOUND = 0
    RUNNING = 1
    PENDING = 2
    UNKNOWN = 3

class BricsSlurmSpawner(SlurmSpawner):
    """
    Custom SlurmSpawner for the Brics project with tailored environment variables
    and a custom batch script for job submission.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.log.info("Initializing BricsSlurmSpawner")
    
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
    
        # Prepare substitution variables for templates using req_xyz traits
    def get_req_subvars(self):
        reqlist = [t for t in self.trait_names() if t.startswith("req_")]
        subvars = {}
        for t in reqlist:
            subvars[t[4:]] = getattr(self, t)
        if subvars.get("keepvars_extra"):
            subvars["keepvars"] += "," + subvars["keepvars_extra"]
        return subvars
    
    async def query_job_status(self):
        """Check job status, return JobStatus object."""
        self.log.debug(f"Entering BricsSlurmSpawner.query_job_status(). self.job_id: {self.job_id}")
        if self.job_id is None or len(self.job_id) == 0:
            self.job_status = ""
            return JobStatus.NOTFOUND
        
        # Introduce a delay to allow the job to start
        delay_seconds = 5  # Adjust this based on how long it typically takes for jobs to start
        self.log.debug(f"BricsSlurmSpawner Delaying job status query by {delay_seconds} seconds to allow the job to start.")
        await asyncio.sleep(delay_seconds)  # Delay the query

        subvars = self.get_req_subvars()
        subvars["job_id"] = self.job_id
        cmd = " ".join(
            (
                format_template(self.exec_prefix, **subvars),
                format_template(self.batch_query_cmd, **subvars),
            )
        )
        self.log.debug("Spawner querying job: " + cmd)
        try:
            cmd = f"squeue -j {self.job_id}"
            self.log.debug(f"BricsSlurmSpawner.query_job_status(): {cmd}")
            self.job_status = await self.run_command(cmd)
            self.log.debug(f"BricsSlurmSpawner.query_job_status(): {self.job_status}")

            # Extract the job status using the parsing function
            job_status_code = parse_job_status(self.job_status, self.job_id)

            if job_status_code == "R":
                return JobStatus.RUNNING
            elif job_status_code in ["PD", "CF"]:  # Pending or Configuring
                return JobStatus.PENDING
            elif job_status_code is None:
                return JobStatus.NOTFOUND
            else:
                return JobStatus.UNKNOWN

        except RuntimeError as e:
        # e.args[0] is stderr from the process
            self.job_status = e.args[0]
        except Exception as ex:
            self.log.error(f"Error querying job {self.job_id}: {ex}")
            self.job_status = ""
        return JobStatus.UNKNOWN
    
    async def run_command(self, cmd, input=None, env=None):
        self.log.debug(f"BricsSlurmSpawner.run_command(): {cmd}")
        proc = await asyncio.create_subprocess_shell(
            cmd,
            env=env,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        inbytes = None

        if input:
            inbytes = input.encode()
            self.log.debug(f"BricsSlurmSpawner.run_command() inbytes: {inbytes}")
        try:
            out, eout = await proc.communicate(input=inbytes)
            self.log.debug(f"BricsSlurmSpawner.run_command() out from communicate: {out}")
            self.log.debug(f"BricsSlurmSpawner.run_command() eout from communicate: {eout}")
        except:
            self.log.debug("Exception raised when trying to run command: %s" % cmd)
            proc.kill()
            self.log.debug("Running command failed, killed process.")
            try:
                out, eout = await asyncio.wait_for(proc.communicate(), timeout=2)
                out = out.decode().strip()
                eout = eout.decode().strip()
                self.log.error("Subprocess returned exitcode %s" % proc.returncode)
                self.log.error("Stdout:")
                self.log.error(out)
                self.log.error("Stderr:")
                self.log.error(eout)
                raise RuntimeError(f"{cmd} exit status {proc.returncode}: {eout}")
            except asyncio.TimeoutError:
                self.log.error(
                    "Encountered timeout trying to clean up command, process probably killed already: %s"
                    % cmd
                )
                return ""
            except:
                self.log.error(
                    "Encountered exception trying to clean up command: %s" % cmd
                )
                raise
        else:
            eout = eout.decode().strip()
            err = proc.returncode
            if err != 0:
                self.log.error("Subprocess returned exitcode %s" % err)
                self.log.error(eout)
                raise RuntimeError(eout)
        self.log.debug(f"BricsSlurmSpawner.run_command() out to return: {out}")
        out = out.decode().strip()
        self.log.debug(f"BricsSlurmSpawner.run_command() out to return: {out}")
        return out

    async def start(self):
        self.log.debug("Entering BricsSlurmSpawner.start()")
        """Start the process"""
        self.ip = self.traits()["ip"].default_value
        self.log.debug(f"BricsSlurmSpawner IP: {self.ip}")

        self.port = self.traits()["port"].default_value
        self.log.debug(f"BricsSlurmSpawner Port: {self.port}")

        if self.server:
            self.server.port = self.port

        await self.submit_batch_script()

        # We are called with a timeout, and if the timeout expires this function will
        # be interrupted at the next yield, and self.stop() will be called.
        # So this function should not return unless successful, and if unsuccessful
        # should either raise and Exception or loop forever.
        self.log.debug(f"BricsSlurmSpawner Get self.job_id: {self.job_id}")

        if len(self.job_id) == 0:
            raise RuntimeError(
                "Jupyter batch job submission failure (no jobid in output)"
            )
        while True:
            status = await self.query_job_status()

            self.log.debug(f"BricsSlurmSpawner query_job_status: {status}")

            if status == JobStatus.RUNNING:
                break
            elif status == JobStatus.PENDING:
                self.log.debug("Job " + self.job_id + " still pending")
            elif status == JobStatus.UNKNOWN:
                self.log.debug("Job " + self.job_id + " still unknown")
            else:
                self.log.warning(
                    "Job "
                    + self.job_id
                    + " neither pending nor running.\n"
                    + self.job_status
                )
                self.clear_state()
                raise RuntimeError(
                    "The Jupyter batch job has disappeared"
                    " while pending in the queue or died immediately"
                    " after starting."
                )
            await asyncio.sleep(self.startup_poll_interval)

        self.ip = self.state_gethost()
        while self.port == 0:
            await asyncio.sleep(self.startup_poll_interval)
            # Test framework: For testing, mock_port is set because we
            # don't actually run the single-user server yet.
            if hasattr(self, "mock_port"):
                self.port = self.mock_port
            # Check if job is still running
            status = await self.poll()
            if status:
                raise RuntimeError(
                    "The Jupyter batch job started"
                    " but died before launching the single-user server."
                )

        self.db.commit()
        self.log.info(
            "Notebook server job {} started at {}:{}".format(
                self.job_id, self.ip, self.port
            )
        )

        return self.ip, self.port

