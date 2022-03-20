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
import logging

from rec.lib.launcher import Launcher
from rec.lib.environment import Environment


def parse_arguments():
    """
    Parse the arguments given on the command line.
    """

    parser = argparse.ArgumentParser(prog='Runtime Environment Capture')

    # general flags
    parser.add_argument('-v', '--version',
                        action='version',
                        version='%(prog)s 0.2.0',
                        help='Print version of REC')

    parser.add_argument('--verbose-version',
                        dest='verbose_version',
                        action='store_true',
                        help='captures full output of --version command'
                             ' rather than just the first line')

    parser.add_argument('-l', '--launcher',
                        action='store',
                        default='cli',
                        choices=['cli', 'shell', 'bash', 'slurm', 'sge'],
                        help='sets runtime launcher for script')

    parser.add_argument('-n', '--name',
                        action='store',
                        help='sets job name')

    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='enables additional logging')

    parser.add_argument('--env-type',
                        dest='env_type',
                        choices=['spack'],
                        help='specify an environment type'
                             ' also requires the --env-file flag')

    parser.add_argument('--env-file',
                        dest='env_file',
                        action='store',
                        help='specify an environment file path'
                             ' also requires the --env-type flag')

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

    # Set logging level
    if arguments.debug:
        logging.basicConfig(format='%(message)s',
                            level=logging.DEBUG)

    # ensures that both environment
    # flags are specified if one flag is
    if arguments.env_type is not None:
        if arguments.env_file is None:
            print("If specifying a environment type,"
                  " you must specify an environment file"
                  " using the `--env-file` flag.")
            sys.exit()
    if arguments.env_file is not None:
        if arguments.env_type is None:
            print("If specifying a environment file,"
                  " you must specify an environment type"
                  " using the `--env-type` flag.")
            sys.exit()

    # Store reproducibility results as json object
    results = {}

    # Stores how job is launched
    runtime_mode = None

    # record results
    if arguments.name:
        results['name'] = arguments.name
    else:
        results['name'] = 'rec-' + datetime.now().strftime("%H-%M-%S")

    # initialize environment
    env = Environment(name=results['name'],
                      env_type=arguments.env_type,
                      env_file=arguments.env_file)
    results['hostname'] = env.hostname
    results['architecture'] = env.architecture
    results['environment'] = env.environment

    # collect information about the environment
    if arguments.env_type is not None:
        results['env_type'] = arguments.env_type
        with open(arguments.env_file, 'r', encoding="utf-8") as file:
            results['env_file'] = file.read()
        results['env_setup_log'] = env.env_install_log

    # initialize launcher
    launcher = Launcher(arguments.launcher)
    results['runtime_mode'] = launcher.info()
    runtime_mode = launcher.mode

    # store information on executables
    results['executables'] = {}

    # hashes input (script or file)
    if arguments.launcher == 'cli':
        # gets hash of CLI input to REC
        to_encode = "".join(arguments.script)
        results['hash'] = sha256(to_encode.encode('ascii')).hexdigest()

        # gets version of first executable in command
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

        # captures information on each executable in script
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

    # record time program starts
    start_time = datetime.now()

    # launch job
    script_result = subprocess.run(script,
                                   capture_output=True,
                                   check=True)

    # record time program ends
    end_time = datetime.now()

    results['start_time'] = start_time.strftime("%H:%M:%S")
    results['end_time'] = end_time.strftime("%H:%M:%S")

    results['script_output'] = script_result.stdout.decode('utf-8')

    with open(results['name']+'.out', 'w', encoding="utf-8") as file:
        json.dump(results, file, indent=4)


if __name__ == '__main__':
    main()
