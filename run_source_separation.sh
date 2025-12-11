#!/bin/bash


#SBATCH -J source_separation
#SBATCH --output=out_source_separation.out

enable_lmod
module load container_env python3

crun python -u nonlinear_least_squares.py
