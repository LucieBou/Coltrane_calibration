#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
Coltrane Cost function for Monte-Carlo on Beluga

@author: luciebourreau
@date: 2024/04/03
"""

import sys

sys.path.append('./model')


from coltrane_params import coltrane_params
from coltrane_population import coltrane_population
from select_C4_C6_august_repro import select_C4_C6_august_repro
from cost_function import cost_function

import numpy as np


def coltrane_cost_function(params, forcing, obs):
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
    
    ## Construct the paramosome with the values to test
    p = coltrane_params(**params)

    ## Run Coltrane to create a population and keep the time serie
    pop, popts = coltrane_population(forcing, p, 2)
    
    #### Compute the RMSE between the model and the observations depending on the context
       
    ## Select the adults in August that have reproduced
    select_popts, select_pop = select_C4_C6_august_repro(popts, pop)
    unique = np.unique(select_pop['mask'], return_counts=False)
        
    if 2 in unique: # The run gave adults in august that have reproduced
    
        adults_august_repro = (select_popts['mask'] == 2)
        
        ### Compute the mean reserves, mean weight and mean fullness for those individuals for each strategy
        
        ## Reserves
        adults_august_repro_reserves = select_popts['R'].copy()
        adults_august_repro_reserves[~adults_august_repro] = np.nan
        
        adults_august_repro_mean_reserves = np.nanmean(adults_august_repro_reserves, axis=0)

        # # Transform those reserves from carbon to lipids to match the observations (i.e., mg lip/cop)
        # adults_august_repro_mean_reserves_tranf = adults_august_repro_mean_reserves / (0.9 * 1000)

        ## Weight
        adults_august_repro_weight = select_popts['W'].copy()
        adults_august_repro_weight[~adults_august_repro] = np.nan
        
        adults_august_repro_mean_weight = np.nanmean(adults_august_repro_weight, axis=0)
        
        ### Flatten those values to disregard the strategies and only have a distribution
        # adults_august_repro_mean_reserves_tranf_all = np.concatenate(adults_august_repro_mean_reserves_tranf)
        adults_august_repro_mean_reserves_all = np.concatenate(adults_august_repro_mean_reserves)
        adults_august_repro_mean_weight_all = np.concatenate(adults_august_repro_mean_weight)
        
        ### Compute the costs
        
        ## Raw distributions
        # mod_reserves_trans = adults_august_repro_mean_reserves_tranf_all.copy()
        mod_reserves = adults_august_repro_mean_reserves_all.copy()
        mod_weight = adults_august_repro_mean_weight_all.copy()
        
        # Lipids
        cost_lip, obs_interp_lip, mod_interp_lip, bins_lip = cost_function(obs["total_lipids_ugC"], mod_reserves[~np.isnan(mod_reserves)])
        
        # Fullness
        mod_fullness = mod_reserves/mod_weight
        cost_full, obs_interp_full, mod_interp_full, bins_full = cost_function(obs["fullness_ratio_carbon_volume"], mod_fullness[~np.isnan(mod_fullness)])
        
        ## Fitness weighted distributions
        
        adults_august_repro_popshape = np.any(adults_august_repro, axis=0)
        
        adults_august_repro_fitness = select_pop['F2'].copy()
        adults_august_repro_fitness[~adults_august_repro_popshape] = np.nan 
        adults_august_repro_fitness_all = np.concatenate(adults_august_repro_fitness)
        
        # Lipids
        
        adults_august_repro_mean_reserves_wgt_all = np.column_stack((adults_august_repro_mean_reserves_all, adults_august_repro_fitness_all))
        
        cost_lip_wgt, obs_interp_lip, mod_interp_lip_wgt, bins_lip_wgt = cost_function(obs["total_lipids_ugC"], adults_august_repro_mean_reserves_wgt_all)
        
        # Fullness
        # adults_august_repro_mean_weight_wgt = adults_august_repro_mean_weight * adults_august_repro_fitness
        # adults_august_repro_mean_weight_wgt_all = np.concatenate(adults_august_repro_mean_weight_wgt)
        
        # mod_fullness_wgt = adults_august_repro_mean_reserves_tranf_wgt_all / adults_august_repro_mean_weight_wgt_all
        
        mod_fullness_wgt = np.column_stack((mod_fullness, adults_august_repro_fitness_all))
        cost_full_wgt, obs_interp_full, mod_interp_full_wgt, bins_full_wgt = cost_function(obs["fullness_ratio_carbon_volume"], mod_fullness_wgt)
        ## Median
        
        # Lipids
        med_lip_obs = np.nanmedian(obs["total_lipids_ugC"])
        med_reserves = np.nanmedian(adults_august_repro_mean_reserves_all)
        
        cost_lip_med = np.mean((med_reserves - med_lip_obs) ** 2)
        
        # Fullness
        med_full_obs = np.nanmedian(obs["fullness_ratio_carbon_volume"])
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
        
        out = {'cost': cost, 
                'params': params, 
                'mod_interp': mod_interp,
                'obs_interp': obs_interp,
                'bins': bins,
                'mask': 2}
        
    if (2 not in unique) & (1 in unique): # The run gave individuals that reproduced but that was not adults in august
        
        out = {'cost': None, 
                'params': params, 
                'mod_interp': None,
                'obs_interp': None,
                'bins': None,
                'mask': 1}
    
    if (len(unique)==1) & (unique[0] == 0): # The run didnot gave individuals that have reproduced (but maybe some are adults in august)
        
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

