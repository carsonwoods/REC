# Runtime Environment Capture

This project aims to create a lightweight wrapper around scripts/commands in order to capture details about the program being run for later reproducibility.

## Supported Runtime Options

- CLI
- Shell (bash, zsh, etc)
- Slurm
- SGE

## Getting Started

To run REC, issue the following command:

```shell
python -m [path/to/REC/install] [COMMAND]
```

By default, REC assumes that you will be running and capturing information about a shell command. The _simplest_ way to run REC would be as follows:

```shell
python -m rec echo "Hello World"
```

This will run the command `echo "Hello World"` as a shell command and will capture information about that command.

### Changing Launcher

To change the desired launcher from recording a command to recording a more complex job, REC accepts a `--launcher/-l` flag.
Using this flag, REC can perform launcher specific capture options for supported launchers.
If the job was a Slurm job, REC would launch the job, capture information about the job, and collect information about Slurm itself.
