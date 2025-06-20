# make inputfiles for SWAN

This repository provides helper scripts to create input data for the [SWAN wave model](https://swanmodel.sourceforge.io/).

---

## Overview

- `python/make_SWANforcing_fromwrfout.py`  
  Extracts wind fields from WRF output files and converts them into SWAN-compatible wind forcing input. Also generates a wind field animation (GIF).
  
- `python/make_grid_bathy.py`  
  Loads GEBCO bathymetry and interactively builds a curvilinear grid and bathymetry files for SWAN. Outputs a `.swn` template for reference.
  
- `run/runswan_timelog.sh`  
  Runs SWAN using MPI and logs execution time with a timestamp.

- `setup_env.sh`  
  Creates a Python virtual environment and installs required dependencies.

---

## Prerequisites

- Python 3.x
- WRF output files
- GEBCO bathymetry data
- A compiled SWAN executable (MPI-capable, for use with `runswan_timelog.sh`)

---

## Setup

```bash
bash setup_env.sh
source .venv/bin/activate
```

---

## Usage

1. **Generate wind forcing from WRF:**

   ```bash
   python/python/make_SWANforcing_fromwrfout.py --wrf-dir /path/to/wrfout/ --output-dir ../00_outputdata/
   ```

   This will create:
   - `INPGRID_WIND_for_SWAN.txt`
   - A visual wind field animation (GIF)

2. **Generate grid and bathymetry interactively:**

   ```bash
   python/python/make_grid_bathy.py --output-dir ../00_outputdata/
   ```

   Follow the prompts to define your target domain. This creates:
   - SWAN grid and bathymetry files
   - A template `.swn` file

3. **Run SWAN:**

   ```bash
   bash run/runswan_timelog.sh <num_mpi_procs> <input.swn>
   ```

---

## Directory Structure

```
python/           # Scripts for wind and grid preparation
run/              # SWAN launch script with timing
setup_env.sh      # Setup for Python environment
README.md         # This file
```

---

## License

See [`LICENSE`](./LICENSE) for licensing details.

Just like Riko and Mirai from *Mahou Tsukai Precure!*—who brighten the world with Linkle magic and friendship—you’re free to remix this code, let it sparkle, and add your own enchantment. Just leave a little stardust in the credits so the original magic can keep glowing.

---

## Feedback

Feel free to open issues or submit pull requests. Contributions are very welcome.
