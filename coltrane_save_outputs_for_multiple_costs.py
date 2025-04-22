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
from select_C4_C6_ind_repro import select_C4_C6_repro

import numpy as np
import pickle
from datetime import datetime


def run_coltrane_save_outputs(I0, Ks, KsIA, maxReserveFrac, rm, tdia_exit, tdia_enter, u0, species, preySatVersion, folder_path):
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
        'tdia_exit': tdia_exit,
        'tdia_enter': tdia_enter,
        'preySatVersion': preySatVersion
    }
    
    p = coltrane_params(**params)
    
    ## Run Coltrane to create a population and keep the time serie
    pop, popts = coltrane_population(forcing, p, 2)
    
    ## Select the adults in August that have reproduced
    select_popts = select_C4_C6_repro(popts, pop)
    unique = np.unique(select_popts['mask'], return_counts=False)
    
    ## Initialize the outputs
    outputs = {'params': params, 
               'species': species,
               'C4_yday': [],
               'C5_yday': [],
               'C6_yday': [],
               'C4_reserves_all': [],
               'C5_reserves_all': [], 
               'C6_reserves_all': [],
               'C4_weight_all': [],
               'C5_weight_all': [],
               'C6_weight_all': [],
               'C4_fitness_all': [],
               'C5_fitness_all': [],
               'C6_fitness_all': [],
               'C4_ind_idx': [],
               'C5_ind_idx': [],
               'C6_ind_idx': [],
            }
    
    for i in unique:
        
        if i == 4:
            
            mask = (select_popts['mask'] == i)
            t_idx, i_idx, j_idx = np.where(mask)
        
            ### Compute the mean reserves, mean weight and mean fitness for those individuals for each strategy
            
            ## Reserves
            reserves = select_popts['R'].copy()
            reserves[~mask] = np.nan
            
            reserves_all = reserves[~np.isnan(reserves)]

            ## Weight
            weight = select_popts['W'].copy()
            weight[~mask] = np.nan
            
            weight_all = weight[~np.isnan(weight)]
            
            ## Fitness
            mask_popshape = np.any(mask, axis=0)
            
            fitness = pop['F2'].copy()
            fitness[~mask_popshape] = np.nan 
            
            fitness_all = fitness[~np.isnan(fitness)]
        
            ## Day of the year
            yday = select_popts['t'].copy()
            yday[~mask] = np.nan
            
            yday_all = yday[~np.isnan(yday)]
            
            ## Individual index
            unique_pairs, inverse_idx = np.unique(list(zip(i_idx, j_idx)), axis=0, return_inverse=True)
            
            ind_idx = inverse_idx
        
            ### Save the outputs
            outputs['C4_reserves_all'] = reserves_all
            outputs['C4_weight_all'] = weight_all
            outputs['C4_fitness_all'] = fitness_all
            outputs['C4_yday'] = yday_all
            outputs['C4_ind_idx'] = ind_idx
            
        if i == 5:
            
            mask = (select_popts['mask'] == i)
            t_idx, i_idx, j_idx = np.where(mask)
        
            ### Compute the mean reserves, mean weight and mean fitness for those individuals for each strategy
            
            ## Reserves
            reserves = select_popts['R'].copy()
            reserves[~mask] = np.nan
            
            reserves_all = reserves[~np.isnan(reserves)]

            ## Weight
            weight = select_popts['W'].copy()
            weight[~mask] = np.nan
            
            weight_all = weight[~np.isnan(weight)]
            
            ## Fitness
            mask_popshape = np.any(mask, axis=0)
            
            fitness = pop['F2'].copy()
            fitness[~mask_popshape] = np.nan 
            
            fitness_all = fitness[~np.isnan(fitness)]
        
            ## Day of the year
            yday = select_popts['t'].copy()
            yday[~mask] = np.nan
            
            yday_all = yday[~np.isnan(yday)]
            
            ## Individual index
            unique_pairs, inverse_idx = np.unique(list(zip(i_idx, j_idx)), axis=0, return_inverse=True)
            
            ind_idx = inverse_idx
            
            ### Save the outputs
            outputs['C5_reserves_all'] = reserves_all
            outputs['C5_weight_all'] = weight_all
            outputs['C5_fitness_all'] = fitness_all
            outputs['C5_yday'] = yday_all
            outputs['C5_ind_idx'] = ind_idx
            
        if i == 6:
            
            mask = (select_popts['mask'] == i)
            t_idx, i_idx, j_idx = np.where(mask)
        
            ### Compute the mean reserves, mean weight and mean fitness for those individuals for each strategy
            
            ## Reserves
            reserves = select_popts['R'].copy()
            reserves[~mask] = np.nan
            
            reserves_all = reserves[~np.isnan(reserves)]

            ## Weight
            weight = select_popts['W'].copy()
            weight[~mask] = np.nan
            
            weight_all = weight[~np.isnan(weight)]
            
            ## Fitness
            mask_popshape = np.any(mask, axis=0)
            
            fitness = pop['F2'].copy()
            fitness[~mask_popshape] = np.nan 
            
            fitness_all = fitness[~np.isnan(fitness)]
        
            ## Day of the year
            yday = select_popts['t'].copy()
            yday[~mask] = np.nan
            
            yday_all = yday[~np.isnan(yday)]
            
            ## Individual index
            unique_pairs, inverse_idx = np.unique(list(zip(i_idx, j_idx)), axis=0, return_inverse=True)
            
            ind_idx = inverse_idx
            
            ### Save the outputs
            outputs['C6_reserves_all'] = reserves_all
            outputs['C6_weight_all'] = weight_all
            outputs['C6_fitness_all'] = fitness_all
            outputs['C6_yday'] = yday_all
            outputs['C6_ind_idx'] = ind_idx
    
    ### Save outputs into a file
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f') # The name of the folder will contain the time
    file_path = f'{folder_path}/coltrane_outputs_for_calibration_I0{np.round(params['I0'],3)}_{timestamp}.pkl'

    with open(file_path, 'wb') as file:
        pickle.dump(outputs, file)

if __name__ == '__main__':
    print('Save Coltrane outputs')

    run_coltrane_save_outputs(float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), int(float(sys.argv[6])), int(float(sys.argv[7])), float(sys.argv[8]), sys.argv[9], sys.argv[10], sys.argv[11])
