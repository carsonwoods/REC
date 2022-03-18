"""
REC - Runtime Environment Capture
Maintained by Carson Woods
Copyright 2020-2022
"""

import os
import subprocess


class Launcher():
    """
    Representation of the launcher command
    as an object. Provides various interfaces
    and functionality.
    """

    def __init__(self, name):
        self.name = name
        self.version, self.verbose_version = self.get_version()
        self.mode = self.get_mode()

    def get_version(self):
        """
        Captures the version of launcher
        """

        version = ""
        if self.name == 'cli':
            version = ''
        elif self.name == 'sge':
            # SGE requires special consideration,
            # no verbose version possible currently.
            v_cmd = ['qstat', '--help']
            version = subprocess.run(v_cmd, capture_output=True, check=True)
            version = version.stdout.decode('utf-8').split('\n')[0]
        else:
            v_cmd = [self.name, '--version']
            version = subprocess.run(v_cmd, capture_output=True, check=True)
            version = version.stdout.decode('utf-8')
        return (version.split('\n')[0], version)

    def get_mode(self):
        """
        Identify proper way to launch command
        """

        if self.name == 'slurm':
            runtime_mode = 'sbatch'
        elif self.name == 'sge':
            runtime_mode = 'qsub'
        elif self.name == 'shell':
            runtime_mode = os.getenv('SHELL')
        elif self.name == 'bash':
            runtime_mode = '/bin/bash'
        else:
            runtime_mode = ''
        return runtime_mode

    def info(self, verbose=False):
        """
        Returns a dictionary with all the
        information about the launcher.
        Primarily used in results file.
        """

        info = {}

        # parse name into more readable launcher name
        if self.name == 'shell':
            info['name'] = os.getenv('SHELL') + '_shell'
        if self.name == 'bash':
            info['name'] = 'bash_script'
        if self.name == 'cli':
            info['name'] = 'shell_command'
        else:
            info['name'] = self.name

        # use verbose version if requested
        if verbose:
            info['version'] = self.verbose_version
        else:
            info['version'] = self.version
        return info
