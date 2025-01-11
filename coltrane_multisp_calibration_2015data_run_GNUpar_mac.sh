#!/bin/bash

# -----------------------------------
# SLURM script - Coltrane Calibration
# -----------------------------------

echo "Starting task"

time parallel -j 4 --colsep ',' python -u coltrane_multisp_calibration_lipids_fullness_GNUpar_2015data.py {1} {2} {3} {4} {5} {6} {7} {8} "./" "BB" :::: ./multisp_parameters_2015data_300.txt

echo "Task done"
