#!/bin/bash


#SBATCH -J snr_80_distance_05_grid_6
#SBATCH --output=out_snr_80_distance_05_grid_6.out

enable_lmod
module load container_env python3

crun python -u nonlinear_least_squares.py 80 5 6
