#!/bin/bash


#SBATCH -J snr_80_distance_05_grid_5
#SBATCH --output=out_snr_80_distance_05_grid_5.out

enable_lmod
module load container_env tensorflow-cpu

crun python -u gradient.py 80 5 5
