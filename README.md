# Runtime Environment Capture

This project aims to create a lightweight wrapper around scripts/commands in order to capture details about the program being run for later reproducibility.

## Supported Runtime Options

- CLI
- Shell (bash, zsh, etc)
- Slurm
- SGE

## Instaling REC

REC supports Linux and MacOS, but is primarily geared towards job launchers that are predominantly available on Linux. That being said, some launchers such as Slurm and SGE are not available on MacOS. If you're using a Mac, this likely doesn't mean much to you, but it's worth mentioning.

### Installing using Pip

```bash
pip install runtime-environment-capture
```

## Running REC

To run REC, issue the following command:

```shell
rec [COMMAND]
```

By default, REC assumes that you will be running and capturing information about a shell command. The _simplest_ way to run REC would be as follows:

```shell
rec echo "Hello World"
```

This will run the command `echo "Hello World"` as a shell command and will capture information about that command.

### Changing Launcher

To change the desired launcher from recording a command to recording a more complex job, REC accepts a `--launcher/-l` flag.
Using this flag, REC can perform launcher specific capture options for supported launchers.
If the job was a Slurm job, REC would launch the job, capture information about the job, and collect information about Slurm itself.
