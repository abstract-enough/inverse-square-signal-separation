#!/bin/bash


#SBATCH -J snr_80_distance_10_grid_4
#SBATCH --output=out_snr_80_distance_10_grid_4.out

enable_lmod
module load container_env python3

crun python -u nonlinear_least_squares.py 80 10 4
