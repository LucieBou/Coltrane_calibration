#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compute RMSE cost for each stage and month.

@author: Lucie Bourreau
@date: 2025/04
"""

import sys

sys.path.append('./model')

from RMSE_cost_function import cost_function

import uuid
import pandas as pd
import numpy as np
import time
import pickle
from datetime import datetime, timedelta

def day_to_month(yday_array):
    """from yearday (1–365*n) to month (1–12)"""
    base_date = datetime(2000, 1, 1)  # random year
    return np.array([
        (base_date + timedelta(days=int(d))).month
        for d in yday_array
    ])

def run_cost_function(stages, months, folder_path_calibration, file_model_outputs, file_obs_data, folder_name_store_outputs):
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
            'mod_interp': {}, 
            'obs_interp': {},
            'bins': {},
            'running_time': None,
            'mask': [],
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
            
            obs = obs_stage[['total_lipids_ugC', 'fullness_ratio_carbon_volume']]

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
                fitness_vals = mod_fitness[grouped.index]
                grouped['fitness'] = fitness_vals
            
                mod_lip_fitness = grouped[['reserves', 'fitness']].values
                mod_fullness = grouped['reserves'].values / grouped['weight'].values
                mod_full_fitness = np.column_stack((mod_fullness, grouped['fitness'].values))
                    
                if len(mod_lip_fitness) > 0:
                
                    # Lipid cost
                    cost_lip_wgt, obs_interp_lip, mod_interp_lip_wgt, bins_lip_wgt = cost_function(obs["total_lipids_ugC"], mod_lip_fitness)
                    
                    # Fullness cost
                    cost_full_wgt, obs_interp_full, mod_interp_full_wgt, bins_full_wgt = cost_function(obs["fullness_ratio_carbon_volume"], mod_full_fitness)
                    
                    # Total cost
                    stage_tot_cost = cost_lip_wgt + cost_full_wgt
                    
                    # Save outputs
                    outputs['cost'][f'M{m}_{stage}_lip_wgt_cost'] = cost_lip_wgt
                    outputs['cost'][f'M{m}_{stage}_full_wgt_cost'] = cost_full_wgt
                    outputs['cost'][f'M{m}_{stage}_tot_cost'] = stage_tot_cost

                    outputs['mod_interp'][f'M{m}_{stage}_lip_wgt'] = mod_interp_lip_wgt
                    outputs['mod_interp'][f'M{m}_{stage}_full_wgt'] = mod_interp_full_wgt

                    outputs['obs_interp'][f'M{m}_{stage}_lip'] = obs_interp_lip
                    outputs['obs_interp'][f'M{m}_{stage}_full'] = obs_interp_full

                    outputs['bins'][f'M{m}_{stage}_lip_wgt'] = bins_lip_wgt
                    outputs['bins'][f'M{m}_{stage}_full_wgt'] = bins_full_wgt
        
  
    end_time = time.time()
    running_time = end_time - start_time

    print("\nRunning time (sec):", round(running_time, 2))
    
    outputs['running_time'] = running_time
    
    unique_id = uuid.uuid4().hex[:8]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f') # The name of the folder will contain the time
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
    
    run_cost_function(
        stages=stages,
        months=months,
        folder_path_calibration=folder_path_calibration,
        file_model_outputs=file_model_outputs,
        file_obs_data=file_obs_data,
        folder_name_store_outputs=folder_name_store_outputs
    )
