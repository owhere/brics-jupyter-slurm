#!/bin/bash
#SBATCH --job-name=echo_date    # Job name
#SBATCH --output=date_output.txt  # Output file
#SBATCH --time=0:05:00          # Maximum run time (5 minutes)
#SBATCH --ntasks=1              # Number of tasks (1 task)
#SBATCH --cpus-per-task=1       # Number of CPU cores per task (1 core)

# The command to run every 5 seconds
while true; do
    date
    sleep 5
done