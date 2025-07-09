#!/bin/bash

# -----------------------------------
# SLURM script - Coltrane Calibration
# -----------------------------------

#SBATCH --time=00:40:00
#SBATCH --account=def-fmaps
#SBATCH --job-name=coltrane_costs
#SBATCH --mail-type=ALL
#SBATCH --mail-user=lucie.bourreau.1@ulaval.ca
#SBATCH --ntasks-per-node=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=40
#SBATCH --mem-per-cpu=500M
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
stages=("C4" "C5" "C6")
months=(8)
gamma=5
folder_path_model_outputs="/project/6001619/lucieb/Coltrane_calibration/coltrane_outputs_sim2"
folder_path_calibration="./"
file_obs_data="merged_LOKI2013_ecotaxa_masks_features_for_calibration.csv"
folder_name_store_outputs="MMD_gam5_costs_sim2"

# Separate array items with a comma
stages_str=$(IFS=, ; echo "${stages[*]}")
months_str=$(IFS=, ; echo "${months[*]}")

# List all pickle files
find "$folder_path_model_outputs" -type f -name "*.pkl" > model_output_files_sim2.txt

# Launch run jobs

parallel -j $SLURM_CPUS_PER_TASK \
    python compute_MMD_cost.py "$stages_str" "$months_str" "$folder_path_calibration" {1} "$file_obs_data" "$folder_name_store_outputs" "$gamma" \
    :::: model_output_files_sim2.txt

# Merge pickle files into one
python -u merge_pickle_files.py "$folder_path_calibration$folder_name_store_outputs" "$folder_path_calibration" "merged_MMD_costs_gam5_files_2013data_u0fix_IA_8000sets.pkl"

echo "Task done"
