#!/bin/bash


#SBATCH -J snr_20_distance_02_grid_4
#SBATCH --output=out_snr_20_distance_02_grid_4.out

enable_lmod
module load container_env tensorflow-cpu

crun python -u gradient.py 20 2 4
