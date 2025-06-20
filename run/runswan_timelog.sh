#!/bin/bash

# Usage: bash runswan_timelog.sh [MPI_NUMBER] [SWAN_INPUT_FILENAME]
# If not provided, MPI number and input filename will be prompted interactively.

mpi_num=${1:-$(read -p "Enter number of MPI processes: " x && echo $x)}
input_file=${2:-$(read -p "Enter SWAN input filename: " y && echo $y)}

logfile=runswan_timelog_$(date +%Y%m%d_%H%M%S).log

# Log start time to file
{
  echo "START: $(date)"
} >> "$logfile"

# Run SWAN with time measurement
# Output of SWAN is displayed on screen
# Only the timing info from 'time' is recorded to logfile
{ time bash swanrun -input "$input_file" -mpi "$mpi_num"; } 2> tmp_time.txt

cat tmp_time.txt                         # Show timing info on screen
tail -n 3 tmp_time.txt >> "$logfile"    # Append only real/user/sys time to log
rm tmp_time.txt

# Log end time to file
{
  echo "END: $(date)"
} >> "$logfile"

