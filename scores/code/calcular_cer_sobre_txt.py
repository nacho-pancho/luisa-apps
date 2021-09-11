#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Dada una lista de transcripciones y una lista correspondiente de "ground truth",
este programa recorre una a una y calcula el CER (Character Error Rate) entre transcripción y ground truth.
El CER entre dos secuencias t y g se calcula como:

CER = distance(t,g) / max(|t|,|g|)

donde distance es la distancia de edición (Levenshtein) y |t| es el largo de la secuencia t.

La funcion distance.nlevenshtein(t,g,method=2) es precisamente lo anterior (n es de "normalized", method = 2 indica normalizar por dist maxima)
"""
# ---- importacion de paquetes necesarios --------------------------------------------#
# ---- notar que scores importa muchas bibliotecas más -------------------------------#
import os.path
import argparse
import distance
import numpy as np
#import scores
# ------------------------------------------------------------------------------------#
if __name__ == '__main__':
    ######################## ARGUMENTOS DE LINEA DE COMANDOS #########################
    ##### datadir = donde están los archivos, list = lista de archivos a scorear #####
    ##################################################################################
    ap = argparse.ArgumentParser()
    ap.add_argument("--gt-prefix", type=str, default="",
                    help="path prefix  where to find ground truth files")
    ap.add_argument("--trans-prefix", type=str, default="",
                    help="path prefix  where to find transcription files")
    ap.add_argument("--list", type=str, default="",
                    help="text file where input files are specified")
    ap.add_argument("--outdir", type=str, default=".",
                    help="output directory.")
    ap.add_argument("--gt-suffix", type=str, default=".gt.txt",
                    help="Suffix of ground truth files.")
    ap.add_argument("--trans-suffix", type=str, default=".txt",
                    help="Suffix of transcribed text files.")

    ################################# INICIALIZACIÓN #################################
    args = vars(ap.parse_args())
    print(args)
    gt_prefix    = args["gt_prefix"]
    trans_prefix = args["trans_prefix"]
    gt_suffix    = args["gt_suffix"]
    trans_suffix = args["trans_suffix"]
    out_dir      = args["outdir"]
    list_fname   = args["list"]

    scores = list()
    with open(list_fname) as list_file:
        score_dict = dict()
        nimage = 0
        for relfname in list_file: # para cada elemento de la lista
            nimage = nimage + 1    # proxima imagen
            #
            # nombres de archivos y directorios de entrada y salida
            #
            relfname = relfname.rstrip('\n')
            reldir, fname = os.path.split(relfname)
            fbase, fext = os.path.splitext(fname)

            trans_dir = os.path.join(trans_prefix, reldir)
            gt_dir    = os.path.join(gt_prefix, reldir)

            trans_fname = os.path.join(trans_dir, fbase + trans_suffix)
            gt_fname = os.path.join(gt_dir, fbase + gt_suffix)
            if 0:
                print(f'#{nimage} image={relfname} trans={trans_fname} gt_fname={gt_fname} ', end='')
            else:
                print(f'{relfname:40s}', end=' | ')
            # creamos carpetas de destino si no existen
            
            ftxt = open(trans_fname, 'r')
            trans_text = ftxt.read().strip()
            ftxt.close()
            
            ftxt = open(gt_fname, 'r')
            gt_text = ftxt.read().strip()
            ftxt.close()
            
            score = distance.nlevenshtein(trans_text,gt_text,method=2)
            scores.append(score)
            print(f"{score:8.6f}")
    print('FINISHED ---------------------------------------')
    print('Statistics:')
    S = np.asarray(scores)
    print('\t mean   ',np.mean(S))
    print('\t median ',np.median(S))
    
