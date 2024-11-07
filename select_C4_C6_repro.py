#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Select adults that reproduced

@author: Lucie Bourreau
@date: 2024/11/07
"""

import sys

sys.path.append('./model')

from D_to_stage import D_to_stage
from yearday import yearday
import numpy as np
import copy

def select_C4_C6_repro(popts, pop):
    """
    Select individuals of stage C4 to C6 in August that reproduced (i.e., tEcen not nan)
    by adding a mask key in popts and pop.
    This is specific for the comparison with LOKI images of 2013.
    
    0 --> individuals that has not reproduced
    1 --> individuals that reproduced
    2 --> individuals that reproduced and became C4, C5 or adults

    Parameters
    ----------
    popts: dict
        Population time series from coltrane_population.
    pop: dict
        Population metrics from coltrane_population.

    Returns
    -------
    select_popts: dict
        State variables as in popts with a new key called 'mask'.
    select_pop: dict
        Metrics as in pop with a new key called 'mask'.

    """
    ### Create the mask
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
    
    ### Add the new key to popts
    select_popts = copy.deepcopy(popts)
    select_popts['mask'] = mask_popts
    
    ### Reduce the dimension of the mask to match the ones of pop variables and add it to pop as a new key
    mask_pop = np.max(mask_popts, axis=0)
    
    select_pop = copy.deepcopy(pop)
    select_pop['mask'] = mask_pop

    return select_popts, select_pop