#!/bin/bash


#SBATCH -J snr_40_distance_02_grid_5
#SBATCH --output=out_snr_40_distance_02_grid_5.out

enable_lmod
module load container_env python3

crun python -u nonlinear_least_squares.py 40 2 5
