#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Este programa toma un conjunto de posibles scores de calidad de OCR y los coteja
contra la calidad percibida por un humano.
Para eso se toman 50 imagenes clasificadas manualmente en 5 calidades (1 peor, 5 mejor)
y se comparaa esas calidades manuales con cada score candidato.
La idea es que un score va a ser mejor mientras más se correlacione con la calidad percibida.

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
import matplotlib.pyplot as plt
import numpy as np

#---------------------------------------------------------------------------------------

if __name__ == '__main__':
    #
    # ARGUMENTOS DE LINEA DE COMANDOS
    #
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--datadir", type=str, default="../data/calib",
		    help="path prefix  where to find files")
    ap.add_argument("-l","--list", type=str, default="../data/calib/calib.list",
		    help="text file where input files are specified")
    #
    # INICIALIZACION
    #
    args = vars(ap.parse_args())
    print(args)
    datadir = args["datadir"]
    list_fname = args["list"]
    ocr_points = []
    true_points = []
    num_corte = 12
    X_pre = np.empty((0,num_corte+1),float) #prescores letra para cada archivo
    s_tra = np.empty((0,2),float) #lev and lsstr metrics
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
        manual = list()
        auto = list()
        por_categoria = list()
        for i in range(5):
            por_categoria.append(list())
        for relfname in list_file:
            #
            # proxima imagen
            #
            nimage = nimage + 1
            #
            # nombres de archivos y directorios de entrada y salida
            #
            relfname = relfname.rstrip('\n')
            reldir, fname = os.path.split(relfname)
            fbase, fext = os.path.splitext(fname)

            filedir = os.path.join(datadir, reldir)

            manual_fname = os.path.join(filedir, fbase + '.manual.txt')
            ocr_fname = os.path.join(filedir, fbase + '.ocr.txt')
            print(f'#{nimage} image={relfname} manual={manual_fname} ocr={ocr_fname}', end='')
            #
            # creamos carpetas de destino si no existen
            #
            ftxt = open(manual_fname, 'r')
            manual_text = ftxt.read()
            ftxt.close()
            ftxt = open(ocr_fname, 'r')
            ocr_text = ftxt.read()
            ftxt.close()
            manual_score = int(reldir[0])
            #
            #===========================================================
            #
            #
            #ocr_score = scores.score_dist_uno(ocr_text, 4)

            presc, vecscore = scores.vec_score(ocr_text, w=[0,0, -0.07185048, 0.17346911,  0.20348388, -0.2180258,  -0.12250389,  0.13601592,  0.39779619,  0.29919473, -0.01594464,  0.04108278,  0.07234357],corte=num_corte)
            lcs, lev = scores.tra_dist(ocr_text,manual_text)

            X_pre = np.concatenate((X_pre, [np.array(presc)]),axis=0)
            s_tra = np.concatenate((s_tra,[np.array([lcs,lev])]),axis=0)
            ocr_score = vecscore
            #ocr_score = scores.score_dist_uno_exp(ocr_text,4)
            #ocr_score_true = scores.true_score_exp(ocr_text, manual_text, 4)
            ocr_points.append(vecscore)
            true_points.append(lev)
            por_categoria[manual_score-1].append(ocr_score)
            # 
            #===========================================================
            #
            print(f"manual={manual_score}  autoscore={ocr_score}")
            manual.append(manual_score)
            auto.append(ocr_score)
            # fin
            #
        np.save('X_pre.npy',X_pre)
        np.save('s_tra.npy',s_tra)
        plt.figure(figsize=(8,8))
        plt.boxplot(por_categoria,notch=False)
        plt.grid(True)
        plt.xlabel('score manual (1 a 5)')
        plt.ylabel('score automatico (0 a 1)')
        plt.title('Score automático vs. score manual (palabras de 4 o más letras)')
        plt.show()
        #
        # fin para cada archivo en la lista
        #
    plt.figure(figsize=(8, 8))
    plt.plot(ocr_points[0:10], true_points[0:10],'or',label = 'Calidad 1')
    plt.plot(ocr_points[10:20], true_points[10:20], 'ok', label='Calidad 2')
    plt.plot(ocr_points[20:30], true_points[20:30], 'o', label='Calidad 3')
    plt.plot(ocr_points[30:40], true_points[30:40], 'x', label='Calidad 4')
    plt.plot(ocr_points[40:50], true_points[40:50], 'og', label='Calidad 5')
    plt.grid(True)
    plt.legend()
    plt.xlabel('Ocr Score')
    plt.ylabel('True Score')
    plt.title('Inter rater agreement')
    plt.show()

    #
    # fin main
    #
    
#---------------------------------------------------------------------------------------
