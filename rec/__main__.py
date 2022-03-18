#!/bin/python3
"""
REC - Runtime Environment Capture
Maintained by Carson Woods
Copyright 2020-2022
"""


import argparse
import subprocess
import json
import sys
from datetime import datetime
from hashlib import sha256

from rec.lib.launcher import Launcher


def parse_arguments():
    """
    Parse the arguments given on the command line.
    """

    parser = argparse.ArgumentParser(prog='Runtime Environment Capture')

    # general flags
    parser.add_argument('-v', '--version',
                        action='version',
                        version='%(prog)s 0.0.1',
                        help='Print version of REC')

    parser.add_argument('--verbose-version',
                        dest='verbose_version',
                        action='store_true',
                        help='captures full output of --version command'
                             'rather than just the first line')

    parser.add_argument('-l', '--launcher',
                        action='store',
                        default='cli',
                        help='sets runtime launcher for script'
                             ' [slurm, sge, bash, shell, cli]')

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
        sys.exit()

    return arguments


def get_version(cmd, verbose=False):
    """
    Captures the version of the output for an executable command
    """
    version = ""
    if cmd == 'qstat':
        # SGE requires special consideration, no verbose version
        # possible currently.
        v_cmd = [cmd, '--help']
        version = subprocess.run(v_cmd, capture_output=True, check=True)
        version = version.stdout.decode('utf-8').split('\n')[0]
    else:
        v_cmd = [cmd, '--version']
        version = subprocess.run(v_cmd, capture_output=True, check=True)
        version = version.stdout.decode('utf-8')
        if not verbose:
            version = version.split('\n')[0]
    return version


def main():
    """
    REC Main Runtime
    """
    arguments = parse_arguments()

    # Store reproducibility results as json object
    results = {}

    # Record Time Program Starts / Ends
    start_time = datetime.now()
    end_time = None

    # Stores how job is launched
    runtime_mode = None

    # Record Results
    if arguments.name:
        results['name'] = arguments.name + ".out"
    else:
        results['name'] = 'rec-' + start_time.strftime("%H-%M-%S") + ".out"

    # Initialize launcher
    launcher = Launcher(arguments.launcher)
    results['runtime_mode'] = launcher.info()
    runtime_mode = launcher.mode

    # Store information on executables
    results['executables'] = {}

    # Hashes Input (Script or File)
    if arguments.launcher == 'cli':

        # Gets hash of CLI input to REC
        to_encode = "".join(arguments.script)
        results['hash'] = sha256(to_encode.encode('ascii')).hexdigest()

        # Gets version of first executable in command
        cmd = arguments.script[0]
        if cmd not in results['executables'].keys():
            results['executables'][cmd] = {}
        version = get_version(cmd, arguments.verbose_version)
        results['executables'][cmd]['version'] = version
    else:
        # Gets hash of entire file
        hash_value = sha256()
        with open(arguments.script[0], 'rb') as file:
            data = file.read(65536)
            hash_value.update(data)
            while data:
                data = file.read(65536)
                hash_value.update(data)
        results['hash'] = hash_value.hexdigest()

        # Captures information on each executable in script
        with open(arguments.script[0], 'r', encoding="utf-8") as file:
            for line in file:
                if "#!/" in line:
                    continue
                cmd = line.split()[0]
                if len(cmd) > 0:
                    if cmd not in results['executables'].keys():
                        results['executables'][cmd] = {}
                    version = get_version(cmd, arguments.verbose_version)
                results['executables'][cmd]['version'] = version

    # formulate launch command
    if runtime_mode != '':
        script = [runtime_mode] + arguments.script
    else:
        script = arguments.script

    # launch job
    script_result = subprocess.run(script,
                                   capture_output=True,
                                   check=True)

    end_time = datetime.now()
    results['start_time'] = start_time.strftime("%H:%M:%S")
    results['end_time'] = end_time.strftime("%H:%M:%S")

    results['script_output'] = script_result.stdout.decode('utf-8')

    with open(results['name'], 'w', encoding="utf-8") as file:
        json.dump(results, file, indent=4)


if __name__ == '__main__':
    main()
