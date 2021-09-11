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
DATADIR = "../results/"
INDIR = DATADIR + "5.analisis/"
OUTDIR = DATADIR + "6.clustering_ali/"

data = np.load(OUTDIR + "sim_alineadas.npz")
sim = data["arr_0"]
shiftmat = data["arr_1"]
plt.matshow(sim,cmap=plt.get_cmap('hot'))
plt.matshow(shiftmat,cmap=plt.get_cmap('hot'))
N,M = sim.shape
for i in range(N):
    for j in range(i):
        sim[i,j] = sim[j,i]
        shiftmat[i,j] = shiftmat[j,i]

sim = sim - np.min(sim)
sim = sim * (1.0/np.max(sim))
shiftmat = shiftmat - np.min(shiftmat)
shiftmat = (1.0/np.max(shiftmat))*shiftmat
cmap = plt.get_cmap('hot')
io.imsave(OUTDIR + "sim_alineadas.png",cmap(sim))
io.imsave(OUTDIR + "shiftmap.png",cmap(shiftmat))

kmeans = cluster.KMeans(n_clusters=20)
