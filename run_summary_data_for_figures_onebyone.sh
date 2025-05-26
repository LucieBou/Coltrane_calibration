#!/bin/bash

# -----------------------------------
# SLURM script - Coltrane Calibration
# -----------------------------------

#SBATCH --time=00:30:00
#SBATCH --account=def-fmaps
#SBATCH --job-name=coltrane_outputs_figures
#SBATCH --mail-type=ALL
#SBATCH --mail-user=lucie.bourreau.1@ulaval.ca
#SBATCH --ntasks-per-node=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=10
#SBATCH --mem-per-cpu=32G
#SBATCH -o slurm-mem-%j.out
#SBATCH -e slurm-mem-%j.err

module load StdEnv/2023
module load python/3.10 scipy-stack
virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
pip install --no-index --upgrade pip
pip install --no-index -r requirements.txt

echo "Starting task"

PARAMS="./params_to_run_for_figures_cost.txt"
OUTPUTDIR="./coltrane_outputs_figures"
SAVEDIR="./summary_data_for_figures"

# Lancer les jobs en parallèle
find "$OUTPUTDIR" -name "*_pop.pkl" | parallel --jobs $SLURM_CPUS_PER_TASK ' 
	fname=$(basename {})
	echo "Processing file: $fname"
	python summary_data_sp_scenario_one_by_one.py '"$PARAMS"' '"$OUTPUTDIR"' "$fname" '"$SAVEDIR"'
 '


echo "Task done"
