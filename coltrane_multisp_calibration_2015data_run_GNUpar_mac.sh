#!/bin/bash

# -----------------------------------
# SLURM script - Coltrane Calibration
# -----------------------------------

echo "Starting task"

time parallel -j 2 --colsep ',' python -u coltrane_multisp_calibration_lipids_fullness_GNUpar_2015data.py {1} {2} {3} {4} {5} {6} {7} {8} "./" :::: ./multisp_parameters_2015data_smalltest.txt

echo "Task done"
