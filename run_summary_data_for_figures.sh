#!/bin/bash

# -----------------------------------
# SLURM script - Coltrane Calibration
# -----------------------------------

#SBATCH --time=01:00:00
#SBATCH --account=def-fmaps
#SBATCH --job-name=coltrane_costs
#SBATCH --mail-type=ALL
#SBATCH --mail-user=lucie.bourreau.1@ulaval.ca
#SBATCH --ntasks-per-node=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=40G
#SBATCH -o slurm-mem-%j.out
#SBATCH -e slurm-mem-%j.err

echo "Load environment"

module load StdEnv/2023
module load python/3.10 scipy-stack

echo "Virtual environment"

virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate

echo "Install dependencies"

pip install --no-index --upgrade pip
pip install --no-index -r requirements.txt

echo "Starting task"

# Fix the inputs
path_params_df="./params_to_run_for_figures_cost.txt"
path_coltrane_outputs="./coltrane_outputs_figures"
path_save_dir="./summary_data_for_figures"

# Run function
python -u summary_data_sp_scenario_10best_for_figures.py "$path_params_df" "$path_coltrane_outputs" "$path_save_dir"

# Merge files
python -u merge_pickle_files.py "$path_save_dir" "./" "summary_data_10best_figures.pkl"

echo "Task done"
