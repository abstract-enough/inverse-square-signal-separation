#!/bin/bash


#SBATCH -J snr_20_distance_05_grid_4
#SBATCH --output=out_snr_20_distance_05_grid_4.out

enable_lmod
module load container_env python3

crun python -u nonlinear_least_squares.py 20 5 4
