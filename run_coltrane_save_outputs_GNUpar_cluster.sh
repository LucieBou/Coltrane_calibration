#!/bin/bash

# -----------------------------------
# SLURM script - Coltrane Calibration
# -----------------------------------

#SBATCH --time=06:00:00
#SBATCH --account=def-fmaps
#SBATCH --job-name=coltrane_outputs_sim2
#SBATCH --mail-type=ALL
#SBATCH --mail-user=lucie.bourreau.1@ulaval.ca
#SBATCH --ntasks-per-node=1
#SBATCH --nodes=1
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

parallel -j $SLURM_CPUS_PER_TASK --colsep ',' python -u coltrane_save_outputs_for_multiple_costs.py {1} {2} {3} {4} {5} {6} {7} {8} {9} {10} "./coltrane_outputs_sim2" :::: ./multisp_parameters_u0fix_IA_8000.txt

# tail -n 2200 ./multisp_parameters_u0fix_IA_8000.txt | \
# parallel -j $SLURM_CPUS_PER_TASK --colsep ',' \
#     python -u coltrane_save_outputs_for_multiple_costs.py {1} {2} {3} {4} {5} {6} {7} {8} {9} {10} "./coltrane_outputs_sim2"

# parallel -j 2 --colsep ',' python -u coltrane_save_outputs_for_multiple_costs.py {1} {2} {3} {4} {5} {6} {7} {8} {9} {10} "./coltrane_outputs_missing_sim2" :::: ./missing_lines_IA_8000set.txt


echo "Task done"
