#!/bin/bash


#SBaATCH --job-name=Tunneling_test
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --time=3:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1

source ~/data/anaconda3/bin/activate


cd ~/data/tsn_paper/streaming_codes

echo "Start Testing ..................................."

python -u server_HPC.py

