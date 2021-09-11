#!/bin/bash
#SBATCH --job-name=mitrabajo
#SBATCH --ntasks=1
#SBATCH --mem=2048
#SBATCH --time=6:00:00
#SBATCH --tmp=9G
#SBATCH --partition=normal
#SBATCH --qos=normal
#SBATCH --mail-type=ALL
#SBATCH --mail-user=mi@correo

source /etc/profile.d/modules.sh

cd ~/miaplicacion
./mibinario arg1 arg2

