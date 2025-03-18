#!/bin/bash

# -----------------------------------
# SLURM script - Coltrane Calibration
# -----------------------------------

echo "Starting task"

time parallel -j 4 --colsep ',' python -u coltrane_multisp_calibration_lipids_fullness_GNUpar_2013data.py {1} {2} {3} {4} {5} {6} {7} {8} "./" "merged_LOKI2013_ecotaxa_masks_features_for_calibration.csv" :::: ./multisp_parameters_2013data_u0var_20.txt

echo "Task done"
