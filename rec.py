#!/bin/python3

import argparse
import os
import subprocess

def parse_arguments():
    """
    Parse the arguments given on the command line.
    """

    parser = argparse.ArgumentParser(prog='Runtime Environment Capture')

    # general flags
    parser.add_argument('-v', '--version',
                        action='version',
                        version='%(prog)s 0.1',
                        help='Print version of REC')

    parser.add_argument('--slurm',
                        action='store_true',
                        help='launch job with slurm\'s sbatch command')

    parser.add_argument('--sge',
                        action='store_true',
                        help='launch job with SGE\'s qsub command')

    parser.add_argument('--bash',
                        action='store_true',
                        help='[default] treats job as a bash'
                             'script and launches it')

    parser.add_argument('--shell',
                        action='store_true',
                        help='treat job as script of'
                             'current shell and launches it')

    parser.add_argument('--cli',
                        action='store_true',
                        help='treats script argument as a'
                             'command and launches it')

    parser.add_argument('script',
                        nargs='*',
                        action='store',
                        help='launch commands or script file to run')

    arguments = parser.parse_args()

    # check for valid input
    if not arguments.script:
        parser.print_help()
        exit()

    return arguments


if __name__ == '__main__':

    arguments = parse_arguments()

    launch_command = None

    # Parses arguments to select launch mechanism
    # for script or command
    if arguments.slurm:
        launch_command = 'sbatch'
    elif arguments.sge:
        launch_command = 'qsub'
    elif arguments.shell:
        launch_command = os.getenv('SHELL')
    elif arguments.cli:
        launch_command = ''
    else:
        launch_command = '/bin/bash'

    if launch_command != '':
        script= [launch_command] + arguments.script
    else:
        script = arguments.script

    script_result = subprocess.run(script, capture_output=True)

    print(script_result.stdout.decode('utf-8'))

