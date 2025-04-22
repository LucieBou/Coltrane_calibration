#!/bin/bash


echo "Starting task"

# Fix the inputs
stages=("C4" "C5" "C6")
months=(8 9)
folder_path_model_outputs="./coltrane_outputs_sim1"
folder_path_calibration="./"
file_obs_data="merged_LOKI2013_ecotaxa_masks_features_for_calibration.csv"
folder_name_store_outputs="costs_sim1"

# Separate array items with a comma
stages_str=$(IFS=, ; echo "${stages[*]}")
months_str=$(IFS=, ; echo "${months[*]}")

# List all pickle files
find "$folder_path_model_outputs" -type f -name "*.pkl" > model_output_files_sim1.txt

# Run jobs
parallel -j 2 \
    python compute_cost_coltrane_obs.py "$stages_str" "$months_str" "$folder_path_calibration" {1} "$file_obs_data" "$folder_name_store_outputs" \
    :::: model_output_files_sim1.txt


# Merge pickle files into one
python -u merge_pickle_files.py "$folder_path_calibration$folder_name_store_outputs" "$folder_path_calibration" "merged_costs_files_2013data_u0fix_4sets.pkl"

echo "Task done"
