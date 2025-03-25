#!/bin/bash

# -----------------------------------
# SLURM script - Coltrane Calibration
# -----------------------------------

#SBATCH --time=23:00:00
#SBATCH --account=def-frmap5
#SBATCH --job-name=coltrane_calibration
#SBATCH --partition=bigmem
#SBATCH --mail-type=ALL
#SBATCH --mail-user=lucie.bourreau.1@ulaval.ca
#SBATCH --cpus-per-task=32
#SBATCH --mem-per-cpu=20G
#SBATCH -o slurm-mem-%j.out
#SBATCH -e slurm-mem-%j.err

module load StdEnv/2023
module load python/3.10 scipy-stack
virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
pip install --no-index --upgrade pip
pip install --no-index -r requirements.txt

echo "Starting task"

parallel -j $SLURM_CPUS_PER_TASK --colsep ',' python -u coltrane_multisp_calibration_lipids_fullness_GNUpar_2013data.py {1} {2} {3} {4} {5} {6} {7} {8} "./" "merged_LOKI2013_ecotaxa_masks_features_for_calibration.csv" :::: ./multisp_parameters_2013data_u0var_8000.txt

python -u merge_pickle_files_2013data.py "./pickle_files/" "./" "merged_files_cluster_2013data_7Y_dtspawn15_NOWArdyna_u0var_8000sets_NewCost.pkl"

echo "Task done"
