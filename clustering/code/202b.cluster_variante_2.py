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
INDIR = DATADIR + "5.analisis_v0/"
OUTDIR = DATADIR + "6.clustering_2/"
MAXDESP = 50

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
M,N = intensidad_de_filas.shape
M2 = M + MAXDESP*2+1
N2 = N

intensidades_alineadas = np.zeros((M2,N2))
intensidades_alineadas[MAXDESP:(MAXDESP+M),:] = intensidad_de_filas[:,:N2]
offset = MAXDESP
sim = np.zeros((N2,N2))
shiftmat = np.zeros((N2,N2))
for i in range(N2):
    x = intensidades_alineadas[:,i]
    for j in range(i+1,N2):
        y = intensidades_alineadas[:,j]
        mindist = np.sum(np.abs(x-y)).astype(np.int)
        minshift = 0
        for shift in range(-MAXDESP,0):
            d = np.sum(np.abs(x-np.roll(y,shift))).astype(np.int)
            if d < mindist:
                mindist = d
                minshift = shift
        for shift in range(1,MAXDESP+1):
            d = np.sum(np.abs(x-np.roll(y,shift))).astype(np.int)
            if d < mindist:
                mindist = d
                minshift = shift
        print i,j,minshift,mindist
        sim[i,j] = mindist
        shiftmat[i,j] = minshift

np.savez(OUTDIR + "sim_alineadas.npz",sim,shiftmat)
plt.matshow(sim)
plt.matshow(shiftmat)
