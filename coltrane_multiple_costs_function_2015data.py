#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
Coltrane Cost function

@author: luciebourreau
@date: 2024/11/05
"""

import sys

sys.path.append('./model')

from coltrane_params import coltrane_params
from coltrane_population import coltrane_population
from cost_function import cost_function
from D_to_stage import D_to_stage

import numpy as np

def coltrane_cost_function(params, forcing, obs):
    """
    Cost function for the Coltrane model. 
    Because data are from different month, the aim is to compute a RMSE between the observed distribution and
    the modeled one for each month and then add them to have the final cost.
    It is possible to put different weight for each RMSE if we want.

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
    
    #### ----------------- RUN THE MODEL

    # Construct the paramosome with the values to test
    p = coltrane_params(**params)

    # Run Coltrane to create a population and keep the time serie
    pop, popts = coltrane_population(forcing, p, 2)
    
    #### ----------------- COMPUTE RMSE BETWEEN MODEL AND OBS

    ## Create a mask to keep only C4 to adult stages that have reproduced in the model

    mask_popts = np.zeros_like(popts['D']) # Initialize the mask with zeros
    reproduced = np.where(~np.isnan(pop['tEcen'])) # Identify which compupods reproduced (i.e., tEcen is not nan)
    mask_popts[:, reproduced[0], reproduced[1]] = 1 # Update the mask to have 1 for individuals that reproduced

    popts['stage'] = np.zeros_like(popts['D']) # Add a new key to popts to have the stage
    for i in range(0,popts['D'].shape[2]):
        popts['stage'][:,:,i] = D_to_stage(popts['D'][:,:,i]) # Fill this new key

    C4_C6_stage = np.zeros_like(popts['D'])
    for i in range(0,popts['D'].shape[2]):
        C4_C6_stage[:,:,i] = np.where(popts['stage'][:,:,i] >= 11, 1, 0) # Identify the individuals of stage C4 to adults

    mask_popts[(C4_C6_stage == 1) & (mask_popts == 1)] = 2 # 1 if they reproduced, 2 if they reproduced and are C4, C5 or adults
    
    
    

