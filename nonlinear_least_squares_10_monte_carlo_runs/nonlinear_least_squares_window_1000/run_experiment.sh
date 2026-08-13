#!/bin/bash

for f in ./run_s*; do
  sbatch $f
done
