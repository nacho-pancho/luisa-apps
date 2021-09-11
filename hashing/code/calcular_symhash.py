#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Plantilla de archivo para trabajar en los distintos proyectos de LUISA
Esta plantilla no hace mas que abrir una lista de archivos, leerlos uno
por uno y guardar una copia en un directorio especificado.

Los requisitos mínimos para correr este script es tener instalados
los siguientes paquetes de Python 3.
Se recomienda utilizar el manejador de paquetes de Python3, pip3:

numpy
pillow 
matplotlib

Se recomienda también el siguiente paquete:

scipy

@author: nacho
"""
#
# # paquetes base de Python3 (ya vienen con Python)
#
# import os
import os.path
import sys
import time
import argparse
import scores
#
# bibliotecas adicionales necesarias
#
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

#---------------------------------------------------------------------------------------

if __name__ == '__main__':
    #
    # ARGUMENTOS DE LINEA DE COMANDOS
    #
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--datadir", type=str, default="/luisa",
		    help="path prefix  where to find files")
    ap.add_argument("-o","--outdir", type=str, default="../results",
		    help="where to store results")
    ap.add_argument("-l","--list", type=str, default="",
		    help="text file where input files are specified")
    #
    # INICIALIZACION
    #
    args = vars(ap.parse_args())
    prefix = args["datadir"]
    outdir = args["outdir"]
    list_file = args["list"]
    #
    # abrimos lista de archivos
    # la lista es un archivo de texto con un nombre de archivo
    # en cada linea
    #
    with open(list_file) as fl:
        t0 = time.time()
        nimage = 0
        #
        # repetimos una cierta operación para cada archivo en la lista
        #
        for relfname in fl:
            #
            # proxima imagen
            #
            nimage = nimage + 1        
            #
            # nombres de archivos y directorios de entrada y salida
            #
            relfname = relfname.rstrip('\n')
            reldir,fname = os.path.split(relfname)
            fbase,fext = os.path.splitext(fname)
            foutdir = os.path.join(outdir,reldir)
            debugdir = os.path.join(foutdir,fbase + "_debug")            
            #
            # creamos carpetas de destino si no existen
            #
            if not os.path.exists(foutdir):
                os.makedirs(foutdir)

            output_fname = os.path.join(foutdir,fname)
            input_fname = os.path.join(prefix,relfname)
            #
            # leemos imagen
            #
            Ipil = Image.open(input_fname)
            I    = np.array(Ipil,dtype=np.int)
            N = np.prod(I.size)
            #---------------------------------------------------
            # hacer algo en el medio
            #---------------------------------------------------
            #
            # 8-way symmetric custom pixel-wise hash
            #
            # XOR of 4-neighbors
            # without center
            I1 = (I[  :-2, 1:-1] + I[ 2:  , 1:-1] + I[ 1:-1,  :-2] + I[ 1:-1, 2:  ])
            I2 = (I[ 2:  , 2:  ] + I[ 2:  ,  :-2] + I[  :-2, 2:  ] + I[  :-2,  :-2])
            # XOR of 4-neigbohrs
            P1 = np.sum(I1 % 2)
            # XOR of 4-diagonal neigbors
            P2 = np.sum(I2 % 2)
            # XOR of 8-neighbors
            P3 = np.sum((I1 + I2) % 2)
            HASH =  P1 ^ P2 ^ P3
            print(f'{input_fname}\t{HASH}')

            #---------------------------------------------------
            #
            # guardamos resultado
            #
        #
        # fin para cada archivo en la lista
        #
    #
    # fin main
    #
    
#---------------------------------------------------------------------------------------
