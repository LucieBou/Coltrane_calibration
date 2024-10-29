#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coltrane lipids and fullness multisp calibration - GNU Parallel

@author: Lucie Bourreau
@date: 2024/05/13
"""

import sys

sys.path.append('./model')

from coltrane_forcing import coltrane_forcing
from coltrane_multiple_costs_function import coltrane_cost_function

import pandas as pd
import time
import pickle
from datetime import datetime


def coltrane_cost_function_wrapper(params, trait, forcing, obs):
    
    try:
        out = coltrane_cost_function(params, trait, forcing, obs)
        
    except Exception as e:
        out = {'cost': None, 
               'params': params, 
               'mod_interp': None,
               'obs_interp': None,
               'bins': None, 
               'mask': 'error'}
        
        print(f"An error occurred in coltrane_cost_function: {e}")
    
    return out

def run_calibration(I0, Ks, maxReserveFrac, rm, tdia_exit, tdia_enter, species, u0, file_path):
    """
    Run the "calibration" that mostly consist of computing a cost between the 
    observed and the modeled traits distributions for a given vector of parameters.
    This function can be easily parallelized.

    Parameters
    ----------
    I0 : float
        Ingestion rate at 0 degree celsius.
    Ks : float
        Half-saturation for ingestion.
    maxReserveFrac : float
        Maximum Reserve Fraction.
    rm : float
        Metabolism relative to prey-saturated ingestion.
    tdia_exit : int
        Diapause exit date (in day of year).
    tdia_enter : int
        Diapause entry date (in day of year).
    species : str
        Species name.
    u0 : float
        Development rate corrected to 0 degree celsius.
    file_path : str
        Path to the rest of the files or scripts.

    Returns
    -------
    outputs : dict
        Outputs.

    """
    
    ## Load the forcing to run Coltrane
    forcing = coltrane_forcing("NOW", 5, file_path)

    ## Load the observations to compare with Coltrane
    obs_all = pd.read_csv(f"{file_path}/copepod_lipids.csv")
    obs_without_MLC5 = obs_all[obs_all['pred'] != 'M. longa C5']
    obs_species = obs_without_MLC5[obs_without_MLC5['spec'] == species]
    obs = obs_species[['totallipid', 'fullnessratio']]

    ## Parameters
    params = {
        'u0': u0,
        'I0': I0,
        'Ks': Ks,
        'maxReserveFrac': maxReserveFrac,
        'rm': rm,
        'tdia_exit': tdia_exit,
        'tdia_enter': tdia_enter
    }    

    start_time = time.time()

    ## Parallelize the simulations and store outputs
    outputs = {'cost': [], 
                'params': [], 
                'mod_interp': [], 
                'obs_interp': [],
                'bins': [],
                'running_time': None,
                'mask': [],
                'species': None
                }
    

    result = coltrane_cost_function_wrapper(params=params, trait='R_and_fullness', forcing=forcing, obs=obs)
    for key, value in result.items():
        outputs[key].append(value)
        
    end_time = time.time()
    running_time = end_time - start_time

    print("\nRunning time:", round(running_time/60/60, 2))
    
    outputs['running_time'] = running_time
    outputs['species'] = species

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f') # The name of the folder will contain the time
    file_path = f'{file_path}/pickle_files/coltrane_multisp_lipids_fullness_calibration_{timestamp}.pkl'

    with open(file_path, 'wb') as file:
        pickle.dump(outputs, file)

   
    return outputs     

if __name__ == '__main__':
    print('Enter inside optimisation')
    # To test
    run_calibration(0.39392328334701276, 0.8498392303370423, 0.7962040794882776, 0.16201464653836029, 90, 250,"C. glacialis", 0.007, "/Users/")
    # To run with a shell file in parallel
    # run_calibration(float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), int(float(sys.argv[5])), int(float(sys.argv[6])), sys.argv[7], float(sys.argv[8]), sys.argv[9])

    
    


