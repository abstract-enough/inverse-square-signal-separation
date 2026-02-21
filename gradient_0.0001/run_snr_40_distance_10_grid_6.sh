#!/bin/bash


#SBATCH -J snr_40_distance_10_grid_6
#SBATCH --output=out_snr_40_distance_10_grid_6.out

enable_lmod
module load container_env tensorflow-cpu

crun python -u gradient.py 40 10 6
