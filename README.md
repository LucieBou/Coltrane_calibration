# Coltrane: parameters calibration from in situ traits measurements
**Lucie Bourreau - August, 2024**

## Introduction

Here you can find the functions required to calculate a cost associated with a vector of parameters for the Coltrane model (an individual trait-based model of Arctic copepods). The cost is calculated from trait data measured from *in situ* LOKI images and simply corresponds to a RMSE between the observed VS modeled trait distributions. The two traits considered are the lipid sac size ('R') and the ratio of lipid sac size to prosome size ('fulness'). The aim to evaluate a large parameter space by sampling it with a Latin hypercube. Then the cost calculation process can be parallelized, as each Coltrane run is independent of the others. 

Note that the codes for calculating the cost are specific to the case presented in **article X**, which depends in particular on the stage of development of the individuals or the date of the year.

The Coltrane model in Python can be found here: https://github.com/LucieBou/Coltrane_python

## How it works

Overview of the functions:

*coltrane_multisp_calibration_lipids_fullness_GNUpar.py* - Contains the run_calibration function, which loads observations and parameter values to be tested, and creates a .pkl file containing cost values and other information. This is the code that can be easily parallelized with GNU, for example.    

*coltrane_multiple_costs_function.py* - Compute the cost for one or two traits ('R' or 'R and fulness') after having selected the modeled individuals comparable with the observed ones (in terms of development stage and date). This function can be adapt according to different datasets.     

*cost_function.py* - Build the traits distributions and compute the RMSE. Note: the if max_obs < 1 if for the fulness trait that range from 0 to 1.     

*create_txt_file_paramosomes_multisp.py* - To create a .txt file with all the vectors of parameters to test. The values are choosen according to the latin_hypercube_samplig.py function.    

**Please, do not hesitate to contact me at lucie.bourreau.1@ulaval.ca for any questions, comments or suggestions.**




