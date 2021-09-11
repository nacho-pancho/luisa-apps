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
import argparse
import scores

#---------------------------------------------------------------------------------------

if __name__ == '__main__':
    #
    # ARGUMENTOS DE LINEA DE COMANDOS
    #
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--datadir", type=str, default="../data",
		    help="path prefix  where to find files")
    ap.add_argument("-t","--txtdir", type=str, default="../results/ocr",
		    help="where the transcription texts are stored.")
    ap.add_argument("-o","--outfile", type=str, default="../results/ocr_scores.csv",
		    help="where to the CSV with the scores")
    ap.add_argument("-l","--list", type=str, default="../data/r0566.list",
		    help="text file where input files are specified")
    #
    # INICIALIZACION
    #
    args = vars(ap.parse_args())
    print(args)
    prefix = args["datadir"]
    txtdir = args["txtdir"]
    outfname = args["outfile"]
    list_fname = args["list"]
    #
    # abrimos lista de archivos
    # la lista es un archivo de texto con un nombre de archivo
    # en cada linea
    #
    with open(list_fname) as list_file:
        nimage = 0
        #
        # para cada elemento de la lista
        #
        for relfname in list_file:
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
            ftxtdir = os.path.join(txtdir,reldir)

            text_fname = os.path.join(ftxtdir,fbase+'.txt')
            print(f'#{nimage} imgfname={relfname} txtfname={text_fname}', end='')
            #
            # creamos carpetas de destino si no existen
            #
            if not os.path.exists(text_fname):
                print('  (no trans)')
                continue
            #ftxt = codecs.open(text_fname,encoding='utf-8')
            ftxt = open(text_fname,'r')            
            text = ftxt.read()
            ftxt.close()
            #
            # separa texto en espacios
            #
            #palabras = [ s.strip(' \n\t\b\r!#$%&/()=?¿¡*+[]{};:,.-_<>|°').lower() for s in tess_text.split() ]
            score = scores.score_ngram(text)
            print(f" score = {score}")
            #
            # calcular scores
            #
            # FALTA: Leopoldus
            #
            # fin
            #
        #
        # fin para cada archivo en la lista
        #
    #
    # fin main
    #
    
#---------------------------------------------------------------------------------------
