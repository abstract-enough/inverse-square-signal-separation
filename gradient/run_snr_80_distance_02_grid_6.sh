#!/bin/bash


#SBATCH -J snr_80_distance_02_grid_6
#SBATCH --output=out_snr_80_distance_02_grid_6.out

enable_lmod
module load container_env tensorflow-cpu

crun python -u gradient.py 80 2 6
