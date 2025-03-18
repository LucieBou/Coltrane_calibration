#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cost function v4

@author: Lucie Bourreau
@date: 2024/03/26
"""


from sklearn.metrics import mean_squared_error
import math
import numpy as np


def cost_function(obs, mod):
    """
    Compute a cost between two distributions.

    Parameters
    ----------
    obs: array
        Observed values.
    mod: array
        Modeled values.

    Returns
    -------
    cost: float
        Cost.
    obs_interp: array
        Interpolated observations on histogramm.
    mod_interp: array
        Interpolated modeled values on histogramm.
    bins: array
        Bins from the histogramm (for figure reproduction).
    """
    
    ## Statistics distributions
    min_obs = np.nanmin(obs)
    max_obs = np.nanmax(obs)
    
    range_obs = max_obs - min_obs
    
    dim_mod = len(np.shape(mod))
    
    if max_obs < 1:
        
        if dim_mod == 1:
            # Compute normalized histograms for mod and obs
            obs_hist, obs_bins = np.histogram(obs, bins=10, range=(min_obs, max_obs), density=True)
            mod_hist, mod_bins = np.histogram(mod.clip(min=min_obs, max=max_obs), bins=10, range=(min_obs, max_obs), density=True)
            
            # Interpolate both histograms
            obs_interp = np.interp(obs_bins[:-1], obs_bins[:-1], obs_hist)
            mod_interp = np.interp(mod_bins[:-1], mod_bins[:-1], mod_hist)
            
            bins = obs_bins
        else:
            # Compute normalized histograms for mod and obs
            obs_hist, obs_bins = np.histogram(obs, bins=10, range=(min_obs, max_obs), density=True)
            mod_hist, mod_bins = np.histogram(np.clip(mod[:,0],a_min=min_obs, a_max=max_obs), 
                                              bins=10, 
                                              range=(min_obs, max_obs), 
                                              density=True, 
                                              weights=mod[:,1])
            
            # Interpolate both histograms
            obs_interp = np.interp(obs_bins[:-1], obs_bins[:-1], obs_hist)
            mod_interp = np.interp(mod_bins[:-1], mod_bins[:-1], mod_hist)
            
            bins = obs_bins
    
    else:
        
        if dim_mod == 1:
            # Compute normalized histograms for mod and obs
            obs_hist, obs_bins = np.histogram(obs, 
                                              bins=15,
                                              #bins=int(range_obs/100), 
                                              range=(min_obs, max_obs), 
                                              density=True)
            mod_hist, mod_bins = np.histogram(mod.clip(min=min_obs, max=max_obs), bins=int(range_obs/0.2), range=(min_obs, max_obs), density=True)
            
            # Interpolate both histograms
            obs_interp = np.interp(obs_bins[:-1], obs_bins[:-1], obs_hist)
            mod_interp = np.interp(mod_bins[:-1], mod_bins[:-1], mod_hist)
            
            bins = obs_bins
            
        else:
            # Compute normalized histograms for mod and obs
            obs_hist, obs_bins = np.histogram(obs, 
                                              bins=15,
                                              #bins=int(range_obs/100), 
                                              range=(min_obs, max_obs), 
                                              density=True)
            mod_hist, mod_bins = np.histogram(np.clip(mod[:,0],a_min=min_obs, a_max=max_obs), 
                                              bins=int(range_obs/0.2), 
                                              range=(min_obs, max_obs), 
                                              density=True,
                                              weights=mod[:,1])
            
            # Interpolate both histograms
            obs_interp = np.interp(obs_bins[:-1], obs_bins[:-1], obs_hist)
            mod_interp = np.interp(mod_bins[:-1], mod_bins[:-1], mod_hist)
            
            bins = obs_bins
    
    # Compute the RMSE
    MSE = mean_squared_error(obs_interp, mod_interp)
    RMSE = math.sqrt(MSE)
    
    cost = RMSE
    
    return cost, obs_interp, mod_interp, bins

