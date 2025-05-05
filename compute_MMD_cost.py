#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compute MMD cost for each stage and month. 

@author: Lucie Bourreau
@date: 2025/05/02
"""

import sys

sys.path.append('./model')

import uuid
import pandas as pd
import numpy as np
import time
import pickle
from datetime import datetime, timedelta
from sklearn.metrics.pairwise import rbf_kernel

def compute_weighted_mmd(X, Y, weights_Y, gamma=None):
    """
    Compute the biased MMD² between X and Y with weights for Y.
    - X: n x d array (observations)
    - Y: m x d array (model predictions)
    - weights_Y: m array (weights, e.g. fitness)
    - gamma: kernel width (if None, will use 1 / median pairwise distance)

    Returns:
        MMD² value
    """
    if gamma is None:
        # Heuristic: median distance between all pairs in concatenated data
        all_data = np.vstack([X, Y])
        pairwise_dists = np.linalg.norm(all_data[:, None, :] - all_data[None, :, :], axis=2)
        gamma = 1.0 / np.median(pairwise_dists[np.triu_indices_from(pairwise_dists, k=1)])

    # Compute kernels
    K_XX = rbf_kernel(X, X, gamma=gamma)
    K_YY = rbf_kernel(Y, Y, gamma=gamma)
    K_XY = rbf_kernel(X, Y, gamma=gamma)

    # Normalize weights
    weights_Y = weights_Y / np.sum(weights_Y)

    # MMD² biased (weighted)
    n = len(X)
    mmd_xx = np.sum(K_XX) / (n * n)
    mmd_yy = np.sum(weights_Y[:, None] * weights_Y[None, :] * K_YY)
    mmd_xy = np.sum(K_XY @ weights_Y) / n

    mmd2 = mmd_xx + mmd_yy - 2 * mmd_xy
    return np.sqrt(mmd2)

def day_to_month(yday_array):
    """from yearday (1–365*n) to month (1–12)"""
    base_date = datetime(2000, 1, 1)  # random year
    return np.array([
        (base_date + timedelta(days=int(d))).month
        for d in yday_array
    ])

def run_cost_function(stages, months, folder_path_calibration, file_model_outputs, file_obs_data, folder_name_store_outputs, gamma):
    """
    Run the "calibration" that mostly consist of computing a cost between the 
    observed and the modeled traits distributions for a given model outputs.
    This function can be easily parallelized using GNU parallel.
    The cost is computed for each stage distinctly and then a pickle file containing the costs is created.

    Parameters
    ----------


    Returns
    -------


    """
    
    print("Enter inside cost function")

    ## Initialize outputs
    outputs = {'cost': {}, 
            'params': [], 
            'mod': {}, 
            'obs': {},
            'running_time': None,
            'species': None
            } 
    
    ## Load the model outputs
    with open(f"{file_model_outputs}", 'rb') as file:
        model = pickle.load(file)
    
    outputs['params'] = model['params']
    
    ## Load the observations to compare with Coltrane
    obs_all = pd.read_csv(f"{folder_path_calibration}{file_obs_data}")
    obs_species = obs_all[obs_all['object_annotation_category'].str.contains(model['species'], case=False, na=False)]
    
    outputs['species'] = model['species']

    ## Compute the costs    
    stage_codes = {'C4': 'civstage',
                   'C5': 'cvstage',
                   'C6': 'female'
                   }
    
    start_time = time.time()
     
    for m in months:
        
        obs_month = obs_species[obs_species['month'] == m]
        
        if obs_month.empty:
            # print(f"No observations for month {m}.")
            continue
        
        for stage in stages:
            
            if stage not in stage_codes:
                # print(f"Not considering stage {stage}.")
                continue
            
            code = stage_codes[stage]
            
            obs_stage = obs_month[obs_month['object_annotation_category'].str.contains(code, case=False, na=False)]
            if obs_stage.empty:
                # print(f"No observations for stage {stage} during month {m}.")
                continue
            
            obs_data = obs_stage[['total_lipids_ugC', 'fullness_ratio_carbon_volume']].values

            mod_reserves = [v for k, v in model.items() if stage in k and 'reserves' in k][0]
            mod_weight = [v for k, v in model.items() if stage in k and 'weight' in k][0]
            mod_fitness = [v for k, v in model.items() if stage in k and 'fitness' in k][0]
            mod_yday = [v for k, v in model.items() if stage in k and 'yday' in k][0]
            mod_ind_idx = [v for k, v in model.items() if stage in k and 'idx' in k][0]
            
            if len(mod_reserves) == 0:
                # print(f"No simulated individuals for stage {stage}.")
                continue

            if len(mod_reserves) > 0:
                
                mod_months = day_to_month(mod_yday)
            
                m_mask = mod_months == m
                
                if not np.any(m_mask):
                    print(f"No simulated individuals for stage {stage} during month {m}.")
                    continue
                
                mod_reserves_m = mod_reserves[m_mask]
                mod_weight_m = mod_weight[m_mask]
                mod_ind_idx_m = mod_ind_idx[m_mask]
                
                df = pd.DataFrame({
                    'ind_idx': mod_ind_idx_m,
                    'reserves': mod_reserves_m,
                    'weight': mod_weight_m
                })
                
                # Mean per ind
                grouped = df.groupby('ind_idx').mean()
            
                # Identify the fitness associated to each ind
                grouped['fitness'] = mod_fitness[grouped.index]
                grouped['fullness'] = grouped['reserves'] / grouped['weight']
            
                # Prepare mod for MMD compute
                mod_data = grouped[['reserves', 'fullness']].values
                mod_weights = grouped['fitness'].values
                
                # Combined both to have the same scaling between obs and mod
                combined = np.vstack([obs_data, mod_data])

                # Min-max scaling
                min_vals = combined.min(axis=0)
                max_vals = combined.max(axis=0)
                obs_scaled = (obs_data - min_vals) / (max_vals - min_vals)
                mod_scaled = (mod_data - min_vals) / (max_vals - min_vals)

                # Compute weighted MMD
                cost = compute_weighted_mmd(obs_scaled, mod_scaled, mod_weights, gamma=gamma)
                
                # Save outputs
                outputs['cost'][f'M{m}_{stage}_cost'] = cost
                outputs['mod'][f'M{m}_{stage}_lip'] = grouped['reserves']
                outputs['mod'][f'M{m}_{stage}_full'] = grouped['fullness']
                outputs['obs'][f'M{m}_{stage}_lip'] = obs_stage['total_lipids_ugC']
                outputs['obs'][f'M{m}_{stage}_full'] = obs_stage['fullness_ratio_carbon_volume']
                
    end_time = time.time()
    running_time = end_time - start_time

    print("\nRunning time (sec):", round(running_time, 2))
    
    outputs['running_time'] = running_time
    
    unique_id = uuid.uuid4().hex[:8]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f') 
    file_path = f'{folder_path_calibration}/{folder_name_store_outputs}/coltrane_multisp_lipids_fullness_calibration_{timestamp}_{unique_id}.pkl'

    with open(file_path, 'wb') as file:
        pickle.dump(outputs, file)
   
    return outputs     

if __name__ == '__main__':
    
    stages = sys.argv[1].split(',') 
    months = [int(m) for m in sys.argv[2].split(',')] 
    folder_path_calibration = sys.argv[3]
    file_model_outputs = sys.argv[4]
    file_obs_data = sys.argv[5]
    folder_name_store_outputs = sys.argv[6]
    gamma = int(sys.argv[7])
    
    run_cost_function(
        stages=stages,
        months=months,
        folder_path_calibration=folder_path_calibration,
        file_model_outputs=file_model_outputs,
        file_obs_data=file_obs_data,
        folder_name_store_outputs=folder_name_store_outputs,
        gamma=gamma
    )
    
    
# plt.scatter(obs_stage['total_lipids_ugC'], obs_stage['fullness_ratio_carbon_volume'], color='red')
# plt.scatter(grouped['reserves'], grouped['fullness'], color='blue')
# plt.title(f"MMD = {cost}")
# plt.show()
