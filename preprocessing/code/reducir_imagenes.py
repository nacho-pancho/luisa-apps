#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Produce versiones reducidas de las imágenes.

Dependencias 

numpy
pillow 
matplotlib

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
#
# bibliotecas adicionales necesarias
#
import numpy as np
from PIL import Image

#---------------------------------------------------------------------------------------

if __name__ == '__main__':
    #
    # ARGUMENTOS DE LINEA DE COMANDOS
    #
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--datadir", type=str, default="/luisa/originales",
		    help="path prefix  where to find files")
    ap.add_argument("-o","--outdir", type=str, default="/luisa/reducidas",
		    help="where to store results")
    ap.add_argument("-l","--list", type=str, default="",
		    help="text file where input files are specified")
    ap.add_argument("-r","--factor", type=int, default=2,
            help="Reducing factor (integer): 2 = half, 4 = quarter, etc. ")
    #
    # INICIALIZACION
    #
    args = vars(ap.parse_args())
    prefix = args["datadir"]
    outdir = args["outdir"]
    list_file = args["list"]
    factor = args["factor"]
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
            print(f'{nimage:8d}\t{relfname}')
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
            Iin  = Image.open(input_fname)
            #
            #---------------------------------------------------
            # reducción
            #---------------------------------------------------
            #
            w,h = Iin.size
            nw,nh = w//factor, h//factor
            Iout = Iin.resize((nw,nh))
            #
            #---------------------------------------------------
            #
            # guardamos resultado
            #
            Iout.save(output_fname,compression="group4",dpi=(150,150))
        #
        # fin para cada archivo en la lista
        #
    #
    # fin main
    #
    
#---------------------------------------------------------------------------------------
