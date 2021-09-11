#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Este programa corre el score desarrollado (vecscore con pesos ajustados por transcripción
manual) sobre una lista de archivos --list en el directorio --datadir.
Los scores son guardados en un archivo de salida 'vecscore_results.txt' formateados como
diccionario.
@author: lagorio
"""
# ---- importacion de paquetes necesarios --------------------------------------------#
# ---- notar que scores importa muchas bibliotecas más -------------------------------#
import os.path
import argparse
import scores
import subprocess
# ------------------------------------------------------------------------------------#
if __name__ == '__main__':
    ######################## ARGUMENTOS DE LINEA DE COMANDOS #########################
    ##### datadir = donde están los archivos, list = lista de archivos a scorear #####
    ##################################################################################
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--imgdir", type=str, default="../data/calib",
                    help="path prefix  where to find files")
    ap.add_argument("-t", "--transdir", type=str, default="../data/calib",
                    help="path prefix  where to find files")
    ap.add_argument("-l", "--list", type=str, default="../data/calib/calib.list",
                    help="text file where input files are specified")
    ap.add_argument("-d", "--outdir", type=str, default="../results/scores",
                    help="output directory for classified images.")
    ap.add_argument("-o", "--outfile", type=str, default="../results/calib.scores",
                    help="text file where output is written.")
    ap.add_argument("-s", "--suffix", type=str, default=".txt",
                    help="Suffix of OCR text files.")
    ################################# INICIALIZACIÓN #################################
    args = vars(ap.parse_args())
    print(args)
    img_dir = args["imgdir"]
    trans_dir = args["transdir"]
    out_dir = args["outdir"]
    list_fname = args["list"]
    ocr_points = []
    # en cada linea de list hay un nombre de archivo con extension .png
    # Los ocr a puntuar se llaman XXX.ocr.txt cuando la imagen se llama XXX.png
    fout = open(args["outfile"],"w")
    with open(list_fname) as list_file:
        score_dict = dict()
        nimage = 0
        for relfname in list_file: # para cada elemento de la lista
            nimage = nimage + 1    # proxima imagen
            # nombres de archivos y directorios de entrada y salida
            relfname = relfname.rstrip('\n')
            reldir, fname = os.path.split(relfname)
            fbase, fext = os.path.splitext(fname)
            filedir = os.path.join(trans_dir, reldir)

            #ocr a puntuar se llaman XXX.ocr.txt cuando la imagen se llama XXX.png
            ocr_fname = os.path.join(filedir, fbase + args['suffix'])
            print(f'#{nimage} image={relfname} ocr={ocr_fname}', end='')
            # creamos carpetas de destino si no existen
            
            ftxt = open(ocr_fname, 'r')
            ocr_text = ftxt.read()
            ftxt.close()
            
            ocr_score = scores.optim_vecscore(ocr_text)
            print(f" score={ocr_score}")
            #score_dict[fbase] = ocr_score #guardo resultado en diccionario
            relbase, _ = os.path.splitext(relfname)
            print(f'{relbase}, {ocr_score}',file=fout)
            #
            # create link to files
            #
            percent_score = 10*int(10*ocr_score)
            pdir = f'{percent_score:02d}'
            findir = os.path.join(img_dir,reldir)
            fimgin = os.path.join(findir,fbase + '.tif')
            foutdir = os.path.join(out_dir,pdir,reldir)
            if not os.path.exists(foutdir):
                os.makedirs(foutdir)
            fimgout = os.path.join(foutdir,fbase + '.tif')
            command = f'ln {fimgin} {fimgout}'
            subprocess.call(command, shell=True)

    fout.close()
    #with open('vecscore_results.txt', 'w') as f: #escribo los resultados en un txt
    #    print(score_dict, file=f)
