#!/bin/python3

import argparse
import os
import subprocess
import json
from datetime import datetime
from hashlib import sha256

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

    parser.add_argument('-n', '--name',
                        action='store',
                        help='sets job name')

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

    # Store reproducibility results as json object
    results = dict()

    # Record Time Program Starts / Ends
    start_time = datetime.now()
    end_time = None

    # Stores how job is launched
    runtime_mode = None

    # Record Results
    if arguments.name:
        results['name'] = arguments.name
    else:
        results['name'] = 'rec_out_' + start_time.strftime("%H:%M:%S")

    # Parses arguments to select launch mechanism
    # for script or command
    if arguments.slurm:
        runtime_mode = 'sbatch'
        results['runtime_mode'] = dict()
        results['runtime_mode']['name'] = 'slurm'
        results['runtime_mode']['version'] = subprocess.run(['sinfo', '-V'],
                                                            capture_output=True).stdout.decode('utf-8')
    elif arguments.sge:
        runtime_mode = 'qsub'
        results['runtime_mode'] = dict()
        results['runtime_mode']['name'] = 'sge'
        sge_version = subprocess.run(['qstat', '--help'], capture_output=True).stdout.decode('utf-8')
        sge_version = sge_version.split('\n')[0]
        results['runtime_mode']['version'] = sge_version
    elif arguments.shell:
        runtime_mode = os.getenv('SHELL')
        results['runtime_mode'] = dict()
        results['runtime_mode']['name'] = runtime_mode + '_script'
        results['runtime_mode']['version'] = subprocess.run([runtime_mode, '--version'],
                                                            capture_output=True).stdout.decode('utf-8')
    elif arguments.cli:
        runtime_mode = ''
        results['runtime_mode'] = dict()
        results['runtime_mode']['name'] = 'shell_command'
        results['runtime_mode']['version'] = ''
    else:
        runtime_mode = '/bin/bash'
        results['runtime_mode'] = dict()
        results['runtime_mode']['name'] = 'bash_script'
        bash_version = subprocess.run(['bash', '--version'], capture_output=True).stdout.decode('utf-8')
        results['runtime_mode']['version'] = bash_version.split('\n')[0]

    # Hashes Input (Script or File)
    if arguments.cli:
        to_encode = ""
        for arg in arguments.script:
            to_encode += arg
        results['hash'] = sha256(to_encode.encode('ascii')).hexdigest()
    else:
        hash = sha256()
        with open(arguments.script[0], 'rb') as f:
            data = f.read(65536)
            hash.update(data)
            while data:
                data = f.read(65536)
                hash.update(data)
        results['hash'] = hash.hexdigest()

    # Formulate Launch Command
    if runtime_mode != '':
        script= [runtime_mode] + arguments.script
    else:
        script = arguments.script

    # Launch Job
    script_result = subprocess.run(script, capture_output=True)

    end_time = datetime.now()
    results['start_time'] =  start_time.strftime("%H:%M:%S")
    results['end_time'] =  end_time.strftime("%H:%M:%S")

    results['script_output'] = script_result.stdout.decode('utf-8')

    with open(results['name'], 'w') as f:
        json.dump(results, f, indent=4)


