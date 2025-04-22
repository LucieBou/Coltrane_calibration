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

def select_C4_C6_repro(popts, pop):
    """
    Select individuals of stage C4 to C6 in August that reproduced (i.e., tEcen not nan)
    by adding a mask key in popts and pop.
    This is specific for the comparison with LOKI images of 2013.
    
    0 --> individuals that has not reproduced
    1 --> individuals that has reproduced but were not C4-C5-C6 in August
    4 --> C4 in August that has reproduced
    5 --> C5 in August that has reproduced
    6 --> C6 in August that has reproduced

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
    
    # Identify the C4 to C6 individuals
    C4 = np.zeros_like(popts['D'])
    C5 = np.zeros_like(popts['D'])
    C6 = np.zeros_like(popts['D'])
    for i in range(0,popts['D'].shape[2]):
        C4[:,:,i] = np.where(popts['stage'][:,:,i] == 11, 1, 0)
        C5[:,:,i] = np.where(popts['stage'][:,:,i] == 12, 1, 0)
        C6[:,:,i] = np.where(popts['stage'][:,:,i] == 13, 1, 0)
    
    ### Update the mask to have 2 for individuals that were adults in august and have reproduced
    mask_popts[(C4 == 1) & (mask_popts == 1)] = 4
    mask_popts[(C5 == 1) & (mask_popts == 1)] = 5
    mask_popts[(C6 == 1) & (mask_popts == 1)] = 6
    
    ### Add the new key to popts
    select_popts = copy.deepcopy(popts)
    select_popts['mask'] = mask_popts
    
    return select_popts

