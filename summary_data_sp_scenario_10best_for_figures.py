#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Store outputs for figures Chapter 1

@author: luciebourreau
"""

import sys

# sys.path.append('./')

from select_C4_C6_ind_repro import select_C4_C6_repro

import gc
import os
import pickle
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def day_to_month(yday_input):
    """Convertit jour de l'année (1–365*n) en mois (1–12).
    Accepte un entier ou un array numpy.
    """
    base_date = datetime(2000, 1, 1)  # année fictive pour conversion
    is_scalar = np.isscalar(yday_input)
    
    yday_array = np.atleast_1d(yday_input)
    flat = yday_array.ravel()
    
    months = np.array([
        (base_date + timedelta(days=int(d))).month
        for d in flat
    ])
    
    months = months.reshape(yday_array.shape)
    
    if is_scalar:
        return int(months[0])  # renvoie un int si entrée scalaire
    return months


def run_summary_sp_scenario_for_figures(path_params_df, path_coltrane_outputs, path_save_dir):

    # Fichiers et dossiers
    params_df = pd.read_csv(path_params_df)

    # Initialiser dictionnaire de listes par (species, scenario)
    #lists = {(sp, sc): [] for sp in ['hyperboreus', 'glacialis'] for sc in ['IA', 'noIA']}
    
    # Lister tous les fichiers pop.pkl
    files = [f for f in os.listdir(path_coltrane_outputs) if f.endswith('_pop.pkl')]
    
    for f in files:
        print(f"file:{f}")
        base = f.replace('_pop.pkl', '')
        pop_path = os.path.join(path_coltrane_outputs, f)
        popts_path = os.path.join(path_coltrane_outputs, f"{base}_popts.pkl")
        if not os.path.exists(popts_path): continue
    
        _, _, species, scenario, sid = base.split('_')
        sid = int(sid)

        # Trouver les bons paramètres
        row = params_df[(params_df['species'] == species) &
                        (params_df['scenario'] == scenario) &
                        (params_df['id'] == sid)]
        if row.empty: continue
        row = row.iloc[0]
    
        # Charger les outputs
        with open(pop_path, 'rb') as f1, open(popts_path, 'rb') as f2:
            pop = pickle.load(f1)
            popts = pickle.load(f2)
    
        # Compute the df for females in august
        results_df1 = {
            'totallipids': [],
            'fullness': [],
            'fitness': [],
        }
        
        select_popts = select_C4_C6_repro(popts, pop)
        mask = select_popts['mask']  # shape (time, cop, strat)
        time_months = day_to_month(select_popts['t'])  # shape (time, cop, strat)
    
        n_cop, n_strat = pop['F2'].shape
    
        for month in [8]:
            for stage in [6]:
                for cop in range(n_cop):
                    for strat in range(n_strat):
                        # masque des temps où l’individu est au stade/stade/mois voulu
                        condition = (time_months[:, cop, strat] == month) & (mask[:, cop, strat] == stage)
                        stage_days = np.where(condition)[0]
    
                        if stage_days.size == 0:
                            continue
    
                        R_vals = select_popts['R'][stage_days, cop, strat]
                        W_vals = select_popts['W'][stage_days, cop, strat]
    
                        R_mean = np.mean(R_vals)
                        W_mean = np.mean(W_vals)
    
                        results_df1['totallipids'].append(R_mean)
                        results_df1['fullness'].append(R_mean / W_mean if W_mean > 0 else np.nan)
                        results_df1['fitness'].append(pop['F2'][cop, strat])
        
        females_august = pd.DataFrame(results_df1)
        
        # Compute the df for all individuals
        results_df2 = {
            'capfrac': pop['capfrac'],
            'genlen': (pop['tEcen']-pop['t0'])/365,
            'Wa': pop['Wa'],
            'fitness': pop['F2']
        }
        
        all_ind = pd.DataFrame({key: value.flatten() for key, value in results_df2.items()})
        
        # Construire le dictionnaire
        d = {
            'species': species,
            'scenario': scenario,
            'id': sid,
            'params': row[['u0', 'I0', 'Ks', 'KsIA', 'maxReserveFrac', 'rm', 'preySatVersion']].to_dict(),
            'cost': row['cost'],
            'females_august': females_august,
            'all_ind': all_ind
        }
    
        # Ajouter à la bonne liste
        #key = (species, scenario)
        #lists[key].append(d)
    
        # Sauvegarde immédiate
        with open(os.path.join(path_save_dir, f"summary_{species}_{scenario}.pkl"), 'wb') as f:
            #pickle.dump(lists[key], f)
            pickle.dump(d, f)

        del pop, popts
        #gc.collect()


if __name__ == '__main__':
    
    run_summary_sp_scenario_for_figures(sys.argv[1], sys.argv[2], sys.argv[3])

    print("Done")
