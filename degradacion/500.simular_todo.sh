#!/bin/bash

# demasiado claro 1
./500.simular_bloques.py --tint=0.5 --noise1=0.5 --noise2=0.5 --blur=0.8 --xscale=2 --yscale=2 --thres=0.6 -g 1 $* 

# demasiado claro 2

#./500.simular_bloques.py --tint=0.5 --noise1=0.5 --noise2=0.34 --blur=0.8 --xscale=3.3 --yscale=3.3 --thres=0.48 $*

# demasiado claro 3

./500.simular_bloques.py --tint=0.5 --noise1=0.5 --noise2=0.34 --blur=0.8 --xscale=3.3 --yscale=3.3 --thres=0.41 $*

# demasiado oscuro / intermedio
./500.simular_bloques.py --tint=0.5 --noise1=0.5 --noise2=0.20 --blur=0.8 --xscale=2 --yscale=2 --thres=0.22 $*

# demasiado oscuro / ruido gordo
./500.simular_bloques.py --tint=0.5 --noise1=0.97 --noise2=0.05 --blur=1.65 --xscale=4.8 --yscale=4.8 --thres=0.05 $*

# demasiado oscuro / ruido fino

./500.simular_bloques.py --tint=0.5 --noise1=0.97 --noise2=0.05 --blur=1.64 --xscale=0.91 --yscale=0.91 --thres=0.05 $*

