#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Latin Hypercube Sampling

@author: luciebourreau
@date: 2024/01/30
"""

from pyDOE2 import lhs

def latin_hypercube_sampling(n, param_bounds):
    """
    Latin Hypercube Sampling

    Parameters
    ----------
    n : int
        Number of parameter sets.
    param_bounds : dict
        Lower and upper boundaries for each parameter.

    Returns
    -------
    param_values : dict
        Parameters values.

    """
    samples = lhs(len(param_bounds), 
                  samples=n,
                  random_state=42
                  #criterion='maximin'
                  )
    
    param_values = {}
    
    for i, (param, bounds) in enumerate(param_bounds.items()):
        param_values[param] = samples[:, i] * (bounds[1] - bounds[0]) + bounds[0]
    
    return param_values
