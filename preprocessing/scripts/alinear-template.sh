#!/bin/bash
#SBATCH --job-name=CAMBIAMEali
#SBATCH --ntasks=1
#SBATCH --mem=2048
#SBATCH --time=20:00:00
#SBATCH --tmp=1G
#SBATCH --partition=besteffort
#SBATCH --qos=besteffort
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ignacio.ramirez.iie@gmail.com

source /etc/profile.d/modules.sh

echo "ROLLO CAMBIAME ALINEADO COMIENZO"
cd ~/luisa-pre/code
python3 ./alinear_paginas.py -d ~/datos/originales -o ~/datos/alineadas -l ~/datos/listas/100/CAMBIAME.list  --force-align 2>&1 > ~/logs/CAMBIAME-alinear.log
#touch ~/logs/CAMBIAME.alineado
if [[ `grep complet ~/logs/CAMBIAME-alinear.log` ]]
then
	touch ~/logs/CAMBIAME.alineado
fi

