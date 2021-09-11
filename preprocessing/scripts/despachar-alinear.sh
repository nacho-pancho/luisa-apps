#!/bin/bash
n=`squeue -u nacho| wc -l`
for i in `cat ~/datos/originales/rollos.list`
do
	echo -n -e "$n\t$i"
	inq=`squeue -u nacho | grep "${i}ali "`
	if [[ $inq ]]
	then
		echo -e "\t(en curso)"	
	elif [[ -f ~/logs/${i}.alineado ]] 
	then
		echo -e "\t(hecho)"
	else
		echo -e "\t(falta)"
		sed "s/CAMBIAME/${i}/g" alinear-template.sh > /tmp/${i}ali.sh
		sbatch /tmp/${i}ali.sh
		let n=n+1
	fi
	#
	# el sistema no nos permite más de 32 pedidos en la cola
	#
	if (( n >= 60 ))
	then
		exit
	fi
done
