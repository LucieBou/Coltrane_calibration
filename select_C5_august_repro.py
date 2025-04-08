#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Select adults in august that reproduced

@author: Lucie Bourreau
@date: 2024/03/13
"""

import sys

sys.path.append('./model')

from D_to_stage import D_to_stage
from yearday import yearday
import numpy as np
import copy

def select_C5_august_repro(popts, pop):
    """
    Select individuals of stage C5 in August that reproduced (i.e., tEcen not nan)
    by adding a mask key in popts and pop.
    This is specific for the comparison with LOKI images of 2013.
    
    0 --> individuals that has not reproduced
    1 --> individuals that reproduced
    2 --> individuals that reproduced and were C5 in august

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
    
    ### Initialize the mask with zeros
    mask_popts = np.zeros_like(popts['D'])
    
    ### Identify which compupods reproduced (i.e., tEcen is not nan)
    reproduced = np.where(~np.isnan(pop['tEcen']))
    
    ### Update the mask to have 1 for individuals that reproduced
    mask_popts[:, reproduced[0], reproduced[1]] = 1
    
    ### Select the adults individual in august
    # Compute the development stage
    popts['stage'] = np.zeros_like(popts['D'])
    for i in range(0,popts['D'].shape[2]):
        popts['stage'][:,:,i] = D_to_stage(popts['D'][:,:,i])
    
    # Identify the august days
    daysofyear = yearday(popts['t'][:,0,0])
    august = np.where((daysofyear >= 220) & (daysofyear <= 250))
    
    # Identify the C5 individuals in August
    C5_august = np.zeros_like(popts['D'])
    for i in range(0,popts['D'].shape[2]):
        C5_august[august,:,i] = np.where(popts['stage'][august,:,i] == 12, 1, 0)
    
    ### Update the mask to have 2 for individuals that were adults in august and have reproduced
    mask_popts[(C5_august == 1) & (mask_popts == 1)] = 2
    
    ### Add the new key to popts
    select_popts = copy.deepcopy(popts)
    select_popts['mask'] = mask_popts
    
    ### Reduce the dimension of the mask to match the ones of pop variables and add it to pop as a new key
    mask_pop = np.max(mask_popts, axis=0)
    
    select_pop = copy.deepcopy(pop)
    select_pop['mask'] = mask_pop
    
    return select_popts, select_pop

