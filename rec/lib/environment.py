"""
REC - Runtime Environment Capture
Maintained by Carson Woods
Copyright 2020-2022
"""

import os
import sys
import subprocess
from logging import debug


class Environment():
    """
    Representation of the job environment
    as an object.
    """

    def __init__(self, name, env_type=None, env_file=None):

        self.name = name
        self.environment = dict(os.environ)
        self.architecture = self.get_arch()
        self.hostname = self.get_hostname()

        self.env_type = env_type
        self.env_file = env_file
        self.env_install_log = None
        self.setup_env()

    def setup_env(self):
        """
        Constructs virtual environment if specified

        Currently supported environment types:
        None, Spack
        """
        if self.env_type == 'spack':
            # creates a Spack virtual environment
            cmd_create = 'spack env create ' + self.name
            cmd_create = cmd_create + " " + self.env_file
            out = subprocess.run(cmd_create,
                                 capture_output=True,
                                 check=True,
                                 shell=True).stdout.decode('utf-8')

            if "Created environment" in out:
                out = out.split('\n')[1].split(' ')[-1]
                self.environment['SPACK_ENV'] = out
                debug("Environment created successfully")

                debug("Installing " + self.name + " environment")

                # constructs complex command to add Spack to environment
                # activate previously created environment
                # and install the environment
                cmd_install = ". " + os.environ['SPACK_ROOT']
                cmd_install = cmd_install + '/share/spack/setup-env.sh;'
                cmd_install = cmd_install + 'spack env activate ' + self.name
                cmd_install = cmd_install + "; spack install"
                out = subprocess.run(cmd_install,
                                     capture_output=True,
                                     check=True,
                                     shell=True).stdout.decode('utf-8')
                self.env_install_log = out
                debug("Environment " + self.name + " installed")
            else:
                del out
                sys.exit("Environment could not be created")

    def get_arch(self):
        """
        Determines machine architecture
        """
        self.architecture = subprocess.run(['arch'],
                                           capture_output=True,
                                           check=True)
        return self.architecture.stdout.decode('utf-8').strip()

    def get_hostname(self):
        """
        Determines machine hostname
        """
        self.hostname = subprocess.run(['hostname'],
                                       capture_output=True,
                                       check=True)
        return self.hostname.stdout.decode('utf-8').strip()
