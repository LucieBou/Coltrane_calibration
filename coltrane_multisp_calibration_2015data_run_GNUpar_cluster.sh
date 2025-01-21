#!/bin/bash

# -----------------------------------
# SLURM script - Coltrane Calibration
# -----------------------------------

#SBATCH --time=00:01:00
#SBATCH --account=def-frmap5
#SBATCH --job-name=coltrane_calibration
#SBATCH --partition=bigmem
#SBATCH --mail-type=ALL
#SBATCH --mail-user=lucie.bourreau.1@ulaval.ca
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=8G
#SBATCH -o slurm-mem-%j.out
#SBATCH -e slurm-mem-%j.err

module load StdEnv/2023
module load python/3.10 scipy-stack
virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
pip install --no-index --upgrade pip
pip install --no-index -r requirements.txt

echo "Starting task"

parallel -j $SLURM_CPUS_PER_TASK --colsep ',' python -u coltrane_multisp_calibration_lipids_fullness_GNUpar_2015data.py {1} {2} {3} {4} {5} {6} {7} {8} "./" "BB" :::: ./multisp_parameters_2015data_oneline_test.txt

python -u merge_pickle_files_beluga.py "./pickle_files/" "./" "merged_files_cluster_2015data_BBforcing_test.pkl"

echo "Task done"
