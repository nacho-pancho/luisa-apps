#!/bin/bash
#SBATCH --job-name=CAMBIAME
#SBATCH --ntasks=1
#SBATCH --mem=2048
#SBATCH --time=10:00:00
#SBATCH --tmp=1G
#SBATCH --partition=besteffort
#SBATCH --qos=besteffort
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ignacio.ramirez.iie@gmail.com

source /etc/profile.d/modules.sh
echo "ROLLO CAMBIAME COMIENZO"
cd ~/luisa-pre/code
python3 ./correr_tesseract_paginas.py -d ~/datos/originales -o ~/datos/transcripciones -l ~/datos/listas/CAMBIAME.list -L ~/logs/CAMBIAME.log
touch ~/logs/CAMBIAME.completo
echo "ROLLO CAMBIAME COMPLETO"

