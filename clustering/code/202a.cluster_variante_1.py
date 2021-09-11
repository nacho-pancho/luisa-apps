#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 12 17:22:41 2018

@author: nacho
"""
# import os.path
import sys
import pnm
import numpy as np
import matplotlib.pyplot as plt
from skimage import io
from os import path
from sklearn import cluster
from subprocess import call

#
# procesar cada imagen en la lista
#
DATADIR = "/datos/data/desaparecidos/"
INDIR= DATADIR + "5.analizadas/"
OUTDIR = DATADIR + "6.clustering/"

intensidad_de_filas          = np.load(INDIR + 'intensidad_de_filas.npy')
intensidades_ordenadas       = np.load(INDIR + 'intensidades_ordenadas.npy')
intensidades_umbralizadas    = np.load(INDIR + 'intensidades_umbralizadas.npy')
distribucion_de_intensidades = np.load(INDIR + 'distribucion_de_intensidades.npy')
distribucion_de_alturas      = np.load(INDIR + 'distribucion_de_alturas.npy')
distribucion_de_bloques      = np.load(INDIR + 'distribucion_de_bloques.npy')

sim_int_umb = np.dot(intensidades_umbralizadas.T, intensidades_umbralizadas)
sim_int_ord = np.dot(intensidades_ordenadas.T, intensidades_ordenadas)
sim_int = np.dot(intensidad_de_filas.T, intensidad_de_filas)
sim_dist_int = np.dot(distribucion_de_intensidades.T, distribucion_de_intensidades)
sim_alt = np.dot(distribucion_de_alturas.T, distribucion_de_alturas)

NCLUSTERS=20

kmeans = cluster.KMeans(n_clusters=20)

if len(sys.argv) < 2:
    lista_de_imagenes = DATADIR + '4.lista.txt'
else:
    lista_de_imagenes = sys.argv[1]

features= {'dist_alt': distribucion_de_alturas,\
    'dist_blk' : distribucion_de_bloques,\
    'dist_int': distribucion_de_intensidades,\
    'int_filas': intensidad_de_filas,\
    'int_filas_ord': intensidades_ordenadas,\
    'int_filas_umb': intensidades_umbralizadas}

#features= {'dist_alt': distribucion_de_alturas}

labels = {}
i = 0
for k,v in features.items():
    print 'Clustering via ',k
    kmeans.fit(v.T)
    labels[k] =  kmeans.labels_
    i = i + 1
    for c in range(NCLUSTERS):
        call("mkdir -p {}/{}/{}".format(OUTDIR,k,c),shell=True)

j = 0
with open(lista_de_imagenes) as fl:
    for fname in fl:
        fname = fname.rstrip('\n')
        fbase = fname[ (fname.find('/')+1):-4 ]
        fcache = INDIR + fbase + "_cache.npz"
        print "looking for " + fcache
        if path.exists(fcache):
            cache = np.load(fcache)
            fname = cache["arr_9"]
            fbase = cache["arr_10"]
            fbase2 = cache["arr_11"]
            for k, v in labels.items():
                cmd = "ln -s {5:s}/{0:s} {1:s}/{2:s}/{3:d}/{4:s}.pbm".format(fname, OUTDIR, k, labels[k][j], fbase2, DATADIR)
                print cmd
                call(cmd,shell=True)
            j = j + 1