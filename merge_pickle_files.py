#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Merge pickle files

@author: Lucie Bourreau
@date: 2024/05/22
"""

import pickle
import os
import sys

def merge_pickle_files(input_files_path, output_file_path, output_file_name):
    """
    Merge multiple pickle files into one.

    Parameters
    ----------
    input_files_path : str
        Path to the folder containing input pickle files.
    output_file_path : str
        Path to the folder where the output pickle file will be saved.
    output_file_name : str
        Name of the output pickle file.

    Returns
    -------
    None.

    """
    # List to store combined data
    combined_data = {'cost': [], 
                     'params': [],
                     'mod_interp': [],
                     'obs_interp': [],
                     'bins': [],
                     'running_time': [],
                     'mask': [],
                     'species': []
                     }

    # Iterate over files in the folder
    for file_name in os.listdir(input_files_path):
        if file_name.endswith(".pkl"):
            file_path = os.path.join(input_files_path, file_name)
            # Read the pickle file and add its content to the combined data dict
            with open(file_path, "rb") as f:
                file_data = pickle.load(f)
                for key, value in file_data.items():
                    combined_data[key].append(value)
                

    # Path to the output pickle file
    output_file_path = os.path.join(output_file_path, output_file_name)

    # Write the combined data to the output pickle file
    with open(output_file_path, "wb") as f:
        pickle.dump(combined_data, f)

    print("Pickle files have been successfully merged!")
    
if __name__ == '__main__':
    print('Start merging')
    
    merge_pickle_files(sys.argv[1], sys.argv[2], sys.argv[3])
    