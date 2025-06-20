#!/bin/bash

# Run SWAN and log its execution time.
#
# Usage: bash runswan_timelog.sh [MPI_NUMBER] [SWAN_INPUT_FILENAME]
#   MPI_NUMBER          Number of MPI processes to use.
#   SWAN_INPUT_FILENAME Path to the SWAN input (.swn) file.
# If an argument is omitted the script will prompt for it interactively.

# Number of MPI processes (prompt if not provided)
mpi_num=${1:-$(read -p "Enter number of MPI processes: " x && echo "$x")}
# Path to the SWAN input file (prompt if not provided)
input_file=${2:-$(read -p "Enter SWAN input filename: " y && echo "$y")}

# Create a unique log file
logfile=runswan_timelog_$(date +%Y%m%d_%H%M%S).log

# Record the start time
{
  echo "START: $(date)"
} >> "$logfile"

# Execute SWAN and measure its runtime
# - swanrun must exist in your PATH
# - SWAN output is displayed on screen
# - only the timing summary from the `time` command is written to the log file
{ time bash swanrun -input "$input_file" -mpi "$mpi_num"; } 2> tmp_time.txt

# Display timing result and append it to the log
cat tmp_time.txt
tail -n 3 tmp_time.txt >> "$logfile"
# Clean up temporary file
rm tmp_time.txt

# Record the end time
{
  echo "END: $(date)"
} >> "$logfile"

