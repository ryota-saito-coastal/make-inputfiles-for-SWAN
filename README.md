# make inputfiles for SWAN

This repository provides helper scripts to create input data for the [SWAN](https://swanmodel.sourceforge.io/) wave model.

## Overview
- `python/make_SWANforcing_fromwrfout.py` extracts wind information from WRF output files and converts it into the SWAN forcing format. The script also generates a GIF animation to visualize the wind fields.
- `python/make_grid_bathy.py` reads GEBCO bathymetry and interactively generates a curvilinear grid and bathymetry files for SWAN. A template `.swn` file is printed and written under the specified output directory (default: `../00_outputdata/`).
- `run/runswan_timelog.sh` launches SWAN with MPI, logging execution time to a timestamped log file.
- `setup_env.sh` creates a Python virtual environment and installs the required Python packages.

## Prerequisites
- Python 3.x
- Access to WRF output files and GEBCO data
- A compiled SWAN executable (MPI capable for `runswan_timelog.sh`)

## Setup
1. Execute `bash setup_env.sh` to create `.venv/` and install dependencies.
2. Activate the environment with `source .venv/bin/activate` before running the Python scripts.

## Usage
1. Edit the paths in `python/make_SWANforcing_fromwrfout.py` to point to your WRF output files. Run the script to produce `INPGRID_WIND_for_SWAN.txt` and related files. Use `--output-dir` to change the destination (default: `../00_outputdata/`).
2. Execute `python/make_grid_bathy.py` and follow the prompts to define the target grid. The bathymetry and grid files will be created in the directory specified by `--output-dir` (default: `../00_outputdata/`).
3. Use the generated files in your SWAN setup and run the model via `bash run/runswan_timelog.sh <mpi_num> <swan_input>`.

## Directory Structure
```
python/    # Python scripts for preparing SWAN input
run/       # Shell script for running SWAN with timing
setup_env.sh  # Convenience script to set up a virtual environment
README.md  # This file
```

## License
See [LICENSE](LICENSE) for licensing details.
---
Just like Riko and Mirai—the magical girls from Mahou Tsukai Precure!—who spark joy with their Linkle magic and unbreakable friendship,
you're free to remix this code, make it shimmer, and craft your own enchanted twist.
Just don’t forget to leave a little stardust in the credits, so the original magic can keep sparkling on.

## Proposed Improvements
The current scripts work but require manual editing and contain Japanese comments. Future tasks include:
- Translate all comments and messages into English for easier collaboration.
- Add command-line arguments to specify file paths instead of hard-coding them (the scripts now accept `--output-dir`).
- Provide docstrings and usage examples for each script.
- Include automated tests for the data generation steps.
- Add a license file and contribution guidelines.

