#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
Run Coltrane for multiple costs and save outputs

@author: luciebourreau
@date: 2024/04/03
"""

import sys

sys.path.append('./model')

from coltrane_params import coltrane_params
from coltrane_forcing import coltrane_forcing
from coltrane_population import coltrane_population

import numpy as np
import pickle
from datetime import datetime


def run_coltrane_save_outputs(u0, I0, Ks, KsIA, maxReserveFrac, rm, preySatVersion, unique_id, species, scenario, folder_path):
    """
    Cost function for the Coltrane model. 

    Parameters
    ----------
    params: dict
        Parameters to test.
    forcing: dict
        Set of forcing, composed of prey and temperature (surface & deep) cycle over several years.
    obs: Dataframe
        Observations of one or the two traits (one or two columns).

    Returns
    -------
    out: dict
        Output containing the RMSE for the specified paramosome and other information.
    """
    
    ## Forcing
    forcing = coltrane_forcing("NOW", 7)
    
    ## Construct the paramosome with the values to test
    params = {
        'u0': u0,
        'I0': I0,
        'Ks': Ks,
        'KsIA': KsIA,
        'maxReserveFrac': maxReserveFrac,
        'rm': rm,
        'tdia_exit': list(range(30, 130, 30)),
        'tdia_enter': list(range(250, 365, 30)),
        'preySatVersion': preySatVersion,
        'min_genlength_years': 1,
        'max_genlength_years': 3,
        'dt_spawn': 30,
    }
    
    p = coltrane_params(**params)
    
    ## Run Coltrane to create a population and keep the time serie
    print("[DEBUG] Running Coltrane with:")
    print("Params:", params)

    try:
        pop, popts = coltrane_population(forcing, p, 2)
    except Exception as e:
        print("ERROR during coltrane_population:", e)
        sys.exit(1)

    #pop, popts = coltrane_population(forcing, p, 2)
    
    print("Run finish start to save")

    pop_file_path = f'{folder_path}/coltrane_outputs_{species}_{scenario}_{unique_id}_pop.pkl'
    popts_file_path = f'{folder_path}/coltrane_outputs_{species}_{scenario}_{unique_id}_popts.pkl'

    with open(pop_file_path, 'wb') as file:
        pickle.dump(pop, file)
        
    with open(popts_file_path, 'wb') as file:
        pickle.dump(popts, file)

if __name__ == '__main__':
    
    print("[DEBUG] Script started with args:", sys.argv)
    
    run_coltrane_save_outputs(float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6]), sys.argv[7], sys.argv[8], sys.argv[9], sys.argv[10], sys.argv[11])

    print("Coltrane outputs saved")
