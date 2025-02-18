#!/bin/bash

# -----------------------------------
# SLURM script - Coltrane Calibration
# -----------------------------------

echo "Starting task"

time parallel -j 4 --colsep ',' python -u coltrane_multisp_calibration_lipids_fullness_GNUpar_2015data.py {1} {2} {3} {4} {5} {6} {7} {8} "./" "BB" "prosome_lipid_segmentation_measures-20241122_PL_metadata_TL_fullness_filter_noMetridia_C4andmore.csv" :::: ./multisp_parameters_2015data_300_largedia.txt

echo "Task done"
