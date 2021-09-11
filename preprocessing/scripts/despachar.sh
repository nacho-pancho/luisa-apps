#!/bin/bash
n=`squeue -A udelar.fing.iie | wc -l`
for i in `cat ~/datos/originales/rollos.list`
do
	echo -n "$n: $i"
	inq=`squeue -A udelar.fing.iie | grep "${i} "`
	if [[ $inq ]]
	then
		echo " (en curso)"	
	elif [[ -f ~/logs/${i}.completo ]] 
	then
		echo " (hecho)"
	else
		echo " (falta)"
		sed "s/CAMBIAME/${i}/g" transcribir-template.sh > /tmp/${i}.sh
		sbatch /tmp/${i}.sh
		let n=n+1
	fi
	#
	# el sistema no nos permite más de 32 pedidos en la cola
	#
	if (( n >= 80 ))
	then
		exit
	fi
done
