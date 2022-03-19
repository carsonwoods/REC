"""
REC - Runtime Environment Capture
Maintained by Carson Woods
Copyright 2020-2022
"""

import os
import subprocess


class Environment():
    """
    Representation of the job environment
    as an object.
    """

    def __init__(self):

        self.environment = dict(os.environ)
        self.architecture = self.get_arch()
        self.hostname = self.get_hostname()


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
