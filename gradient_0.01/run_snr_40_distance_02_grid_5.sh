#!/bin/bash


#SBATCH -J snr_40_distance_02_grid_5
#SBATCH --output=out_snr_40_distance_02_grid_5.out

enable_lmod
module load container_env tensorflow-cpu

crun python -u gradient.py 40 2 5
