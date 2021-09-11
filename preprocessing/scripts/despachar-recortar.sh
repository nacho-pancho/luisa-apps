#!/bin/bash
n=`squeue -u nacho | wc -l`
for i in `cat ~/datos/originales/rollos.list`
do
	echo -n "$n: $i"
	inq=`squeue -u nacho -o %j | grep "${i}rec"`
	if [[ $inq ]]
	then
		echo " (en curso)"	
	elif [[ -f ~/logs/${i}.recortado ]] 
	then
		echo " (hecho)"
	else
		echo " (falta)"
		sed "s/CAMBIAME/${i}/g" recortar-template.sh > /tmp/${i}rec.sh
		sbatch /tmp/${i}rec.sh
		let n=n+1
	fi
	#
	# el sistema no nos permite más de 32 pedidos en la cola
	#
	if (( n >= 120 ))
	then
		exit
	fi
done
