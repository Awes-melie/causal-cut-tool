#!/bin/bash
#SBATCH --nodes=1
#SBATCH --mem=24000
#SBATCH --time=8:00:00

echo "__EXTRACTING G-ESTIMATION__"
python g_estimation.py

echo "__POSTPROCESSING LOG FILE__"
python postprocess_log.py

echo "__COMPLETED__"
