#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create a .txt file of paramosomes

@author: Lucie Bourreau
@date: 2024/05/21
"""

from latin_hypercube_sampling import latin_hypercube_sampling

def params_file(number, storage_path, output_name, preySatVersion):
    """
    Create a parameters.txt file composed of number lines and X columns depending 
    on the number of parameters in the param_bounds variable.

    Parameters
    ----------
    number : int
        Number of parameters sets.
    storage_path : str
        Path where to store the .txt file.

    Returns
    -------
    None.

    """
    
    # Create the paramosomes
    param_bounds = {
        'I0': (0.3, 0.5),
        'Ks': (0.5, 1.5),
        'KsIA': (0.1, 0.8),
        'maxReserveFrac': (0.6, 1),
        'rm': (0.05, 0.25),
        'tdia_exit': (30, 165),
        'tdia_enter': (180, 365)
    }
    
    param_sets = latin_hypercube_sampling(number, param_bounds)
    param_values_list = [{param: param_sets[param][i] for param in param_bounds} for i in range(number)]
    
    # Replicate the parameters list as many times as there are species to calibrate
    
    species = ['Calanus glacialis', 'Calanus hyperboreus']
    dev_rates = [0.007, 0.006]
    
    with open(f"{storage_path}/{output_name}", "w") as fichier:
        
        for species_item, dev_rate_item in zip(species, dev_rates):

            for paramosome in param_values_list:
                
                paramosome['u0'] = dev_rate_item
                paramosome['species'] = species_item
                paramosome['preySatVersion'] = preySatVersion
                
                line = ",".join(str(paramosome[key]) for key in paramosome.keys())
                fichier.write(line + "\n")
    
