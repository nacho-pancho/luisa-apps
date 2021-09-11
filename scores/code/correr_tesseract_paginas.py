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
# paquetes base de Python3 (ya vienen con Python)
#
import os.path
import sys
import time
import argparse
import math
import subprocess
#
# bibliotecas adicionales necesarias
#
import numpy as np


#---------------------------------------------------------------------------------------

TESS_DATA   = "/home/DOCDIC/tesseract/software/TESSDATA_AG/tessdata_fast"
#TESS_CONFIG = f'-l spa --tessdata-dir {TESS_DATA}' 
TESS_CONFIG = '-l spa' 

#---------------------------------------------------------------------------------------

def execute_tesseract(input_file, output_noext, tmpname):
    if input_file[-3:] == 'tif':
        command = f'gm convert -format png "{input_file}" {tmpname}'
        subprocess.call(command, shell=True)
        input_file = tmpname
    command = f'tesseract {TESS_CONFIG} "{input_file}" "{output_noext}"'
    print(command)
    subprocess.call(command, shell=True)

#---------------------------------------------------------------------------------------

if __name__ == '__main__':
    #
    # ARGUMENTOS DE LINEA DE COMANDOS
    #
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--datadir", type=str, default="../data",
		    help="path prefix  where to find files")
    ap.add_argument("-o","--outdir", type=str, default="../results",
		    help="where to store results")
    ap.add_argument("-L","--logfile", type=str, default="../results/r0566.log",
		    help="destination log file.")
    ap.add_argument("-l","--list", type=str, default="../data/r0566.list",
		    help="text file where input files are specified")
    ap.add_argument("-f","--force", type=bool, default=False,
		    help="forzar sobreescritura")
    #
    # INICIALIZACION
    #
    args = vars(ap.parse_args())
    print(args)
    logfname = args["logfile"]
    prefix = args["datadir"]
    outdir = args["outdir"]
    list_file = args["list"]
    _,tmpname = os.path.split(list_file)
    tmpname,_ = os.path.splitext(tmpname)
    tmpname = os.path.join('/tmp',tmpname+'.png')
    #
    # abrimos lista de archivos
    # la lista es un archivo de texto con un nombre de archivo
    # en cada linea
    #
    logfile = open(logfname,'w')

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
            print(f'#{nimage} relfname={relfname} outdir={outdir} fname={fname} fbase={fbase}',end='',file=logfile)
            #
            # creamos carpetas de destino si no existen
            #
            if not os.path.exists(foutdir):
                os.makedirs(foutdir)

            output_fname_noext = os.path.join(foutdir,fbase)
            input_fname = os.path.join(prefix,relfname)
            #
            # leemos imagen
            #
            output_fname = output_fname_noext + '.txt'
            if not os.path.exists(output_fname) or args['force']: 
                execute_tesseract(input_fname,output_fname_noext,tmpname)
                print(' (pronto)',file=logfile)
            else:
                print(' (cache)',file=logfile)
            
            #---------------------------------------------------
            # hacer algo en el medio
            #---------------------------------------------------
            #Iout = Iin.copy()

            #---------------------------------------------------
            #
            # guardamos resultado
            #
            #Iout.save(output_fname)
        #
        # fin para cada archivo en la lista
        #
    logfile.close()
    #
    # fin main
    #
    
#---------------------------------------------------------------------------------------
