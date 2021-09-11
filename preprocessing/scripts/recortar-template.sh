#!/bin/bash
#SBATCH --job-name=CAMBIAMErec
#SBATCH --ntasks=1
#SBATCH --mem=2048
#SBATCH --time=5:00:00
#SBATCH --tmp=1G
#SBATCH --partition=besteffort
#SBATCH --qos=besteffort
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ignacio.ramirez.iie@gmail.com

source /etc/profile.d/modules.sh
cd ~/luisa-pre/code
python3 ./segmentar_paginas.py -d ~/datos/alineadas -o ~/datos/recortadas -l ~/datos/listas/100/CAMBIAME.list 2>&1 > ~/logs/CAMBIAME-recortar.log
if [[ `grep completo ~/logs/CAMBIAME-recortar.log` ]]
then
	touch ~/logs/CAMBIAME.recortado
fi

