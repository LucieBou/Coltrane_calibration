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
from select_C4_C6_repro import select_C4_C6_repro
from yearday import yearday

import numpy as np

def coltrane_cost_function(params, forcing, obs):
    """
    Cost function for the Coltrane model. 
    Because data are from different month, the aim is to compute a RMSE between the observed distribution and
    the modeled one for each month and then add them to have the final cost.
    It is possible to put different weight for each RMSE (each month) if we want.

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

    ## Select the C4 to adult stages that have reproduce
    select_popts, select_pop = select_C4_C6_repro(popts, pop)
    unique = np.unique(select_pop['mask'], return_counts=False)

    ## Isolate the months data from the observation
    obs_month = obs['month']

    ## Create a month mask for the model
    daysofyear = yearday(popts['t'][:,0,0])
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    months = np.zeros_like(daysofyear)
    current_day = 1
    for i, days in enumerate(days_in_month):
        months[(daysofyear >= current_day) & (daysofyear < current_day + days)] = i + 1
        current_day += days

    if 2 in unique: # The run gave adults that have reproduced
        
        adults_repro = (select_popts['mask'] == 2)
        adults_repro_popshape = np.any(adults_repro, axis=0)

        out = {'cost': [],
               'mod_interp': [],
               'obs_interp': [],
               'bins': [],
               'month': [],
               'params': params,
               'mask': 2}

        for m in np.unique(obs_month):
            
            #### Reserves
            # isolate the adults that have reproduce in the months where we have observations
            select_popts_R_m = select_popts['R'][months == m, :, :]
            adults_repro_m = adults_repro[months == m, :, :]

            # Put to NaN the values of non adults that have not reproduce
            reserves = np.where(adults_repro_m, select_popts_R_m, np.nan)

            # Compute the mean over the month for each compupod at each strategy
            mean_reserves = np.nanmean(reserves, axis=0)

            # # Transform those reserves from carbon to lipids to match the observations (i.e., mg lip/cop) (Maps et al., 2014 - Tarling et al., 2022)
            # mean_reserves_lip = mean_reserves / (0.9 * 1000)

            #### Weight
            select_popts_W_m = select_popts['W'][months == m, :, :]
            weight = np.where(adults_repro_m, select_popts_W_m, np.nan)
            mean_weight = np.nanmean(weight, axis=0)

            #### Flatten those values to disregard the strategies and only have a distribution
            mean_reserves_all = np.concatenate(mean_reserves)
            # mean_reserves_lip_all = np.concatenate(mean_reserves_lip)
            mean_weight_all = np.concatenate(mean_weight)

            #### Compute the costs

            # Lipids
            cost_lip, obs_interp_lip, mod_interp_lip, bins_lip = cost_function(obs['apsilon_total_lipids_ugC'][obs['month'] == m], mean_reserves_all[~np.isnan(mean_reserves_all)])

            # Fulness
            mod_fullness = mean_reserves_all/mean_weight_all
            cost_full, obs_interp_full, mod_interp_full, bins_full = cost_function(obs['fullness_ratio_ugC'][obs['month'] == m], mod_fullness[~np.isnan(mod_fullness)])

            #### Fitness weighted distributions
            fitness = np.where(adults_repro_popshape, select_pop['F2'], np.nan)
            fitness_all = np.concatenate(fitness)
            
            # Lipids
            mean_reserves_wgt_all = np.column_stack((mean_reserves_all, fitness_all)) 
            cost_lip_wgt, obs_interp_lip, mod_interp_lip_wgt, bins_lip_wgt = cost_function(obs['apsilon_total_lipids_ugC'][obs['month'] == m], mean_reserves_wgt_all)
            
            # Fullness
            mod_fullness_wgt = np.column_stack((mod_fullness, fitness_all))
            cost_full_wgt, obs_interp_full, mod_interp_full_wgt, bins_full_wgt = cost_function(obs['fullness_ratio_ugC'][obs['month'] == m], mod_fullness_wgt)
            
            #### Median
            
            # Lipids
            med_lip_obs = np.nanmedian(obs['apsilon_total_lipids_ugC'])
            med_reserves = np.nanmedian(mean_reserves_all)
            
            cost_lip_med = np.mean((med_reserves - med_lip_obs) ** 2)
            
            # Fullness
            med_full_obs = np.nanmedian(obs['fullness_ratio_ugC'])
            med_full = np.nanmedian(mod_fullness)
            
            cost_full_med = np.mean((med_full - med_full_obs) ** 2)
            
            # Total cost
            cost_tot = cost_lip + cost_full + cost_lip_wgt + cost_full_wgt + (cost_lip_med/10) + (cost_full_med/10) 

             ### Save the outputs
            
            cost = {'cost_lip': cost_lip,
                    'cost_lip_wgt': cost_lip_wgt,
                    'cost_full': cost_full,
                    'cost_full_wgt': cost_full_wgt,
                    'cost_lip_med': cost_lip_med,
                    'cost_full_med': cost_full_med,
                    'cost_tot': cost_tot,
                    'tot_cost_fit_wgt': cost_lip_wgt+cost_full_wgt,
                    'tot_cost_nonfit_wgt': cost_lip+cost_full}
            
            mod_interp = {'mod_interp_lip': mod_interp_lip,
                          'mod_interp_full': mod_interp_full,
                          'mod_interp_lip_wgt': mod_interp_lip_wgt,
                          'mod_interp_full_wgt': mod_interp_full_wgt,
                          'med_reserves': med_reserves,
                          'med_full': med_full}
            
            obs_interp = {'obs_interp_lip': obs_interp_lip,
                          'obs_interp_full': obs_interp_full,
                          'med_lip_obs': med_lip_obs,
                          'med_full_obs': med_full_obs}
            
            bins = {'bins_lip': bins_lip,
                    'bins_full': bins_full,
                    'bins_lip_wgt': bins_lip_wgt,
                    'bins_full_wgt': bins_full_wgt}
            
            out['cost'].append(cost)
            out['mod_interp'].append(mod_interp)
            out['obs_interp'].append(obs_interp)
            out['bins'].append(bins)
            out['month'].append(m)
    
    if (2 not in unique) & (1 in unique): # The run gave individuals that reproduced but that never became adults
            
        out = {'cost': None, 
                'params': params, 
                'mod_interp': None,
                'obs_interp': None,
                'bins': None,
                'mask': 1}
        
    if (len(unique)==1) & (unique[0] == 0): # The run didnot gave individuals that have reproduced
        
        out = {'cost': None, 
                'params': params, 
                'mod_interp': None,
                'obs_interp': None,
                'bins': None,
                'mask': 0}
        
    if np.count_nonzero(~np.isnan(popts['R'])) == 0: # The run gave no viable individuals, i.e., no one have reserves
        
        out = {'cost': None, 
                'params': params, 
                'mod_interp': None,
                'obs_interp': None,
                'bins': None,
                'mask': np.nan}
    
    return out
