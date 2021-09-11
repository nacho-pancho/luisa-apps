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
import os
from subprocess import call

#
# procesar cada imagen en la lista
#
DATADIR = "../results/"
INDIR = DATADIR + "4.analisis/"
OUTDIR = DATADIR + "6.clustering/intensidades_alineadas/"
MAXDESP = 25

intensidad_de_filas          = np.load(INDIR + 'intensidad_de_filas.npy')

M,N = intensidad_de_filas.shape
M2 = M + MAXDESP*2+1
N2 = N

intensidades_alineadas = np.zeros((M2,N2))
intensidades_alineadas[MAXDESP:(MAXDESP+M),:] = intensidad_de_filas[:,:N2]
offset = MAXDESP
sim = np.zeros((N2,N2))
os.system("mkdir -p "+OUTDIR)
shiftmat = np.zeros((N2,N2))
for i in range(N2):
    x = intensidades_alineadas[:,i]
    nx = 1.0/np.sum(x)
    print "shifting relative to image ",i,
    fcache = OUTDIR + "shiftmat_row_{0:04d}.npz".format(i)
    if os.path.exists(fcache):            
        cache = np.load(fcache)
        shiftmat[i,:] = cache['arr_0']
        print "(cached)"
        continue
    for j in range(i+1,N2):
        y = intensidades_alineadas[:,j]
        ny = 1.0/np.sum(y)
        mindist = np.sum(np.abs(x-y))/(nx*ny)
        minshift = 0
        for shift in range(-MAXDESP,0):
            d = np.sum(np.abs(x-np.roll(y,shift)))/(nx*ny)
            if d < mindist:
                mindist = d
                minshift = shift
        for shift in range(1,MAXDESP+1):
            d = np.sum(np.abs(x-np.roll(y,shift)))/(nx*ny)
            if d < mindist:
                mindist = d
                minshift = shift
        sim[i,j] = mindist
        shiftmat[i,j] = minshift
        sim[j,i] = mindist
        shiftmat[j,i] = minshift
    np.savez(fcache,shiftmat[i,:])
    print "(done)"
    
np.savez(OUTDIR + "sim_alineadas_v1.npz",sim,shiftmat)

sim = sim - np.min(sim)
sim = sim * (1.0/np.max(sim))
shiftmat = shiftmat - np.min(shiftmat)
shiftmat = (1.0/np.max(shiftmat))*shiftmat
cmap = plt.get_cmap('hot')
io.imsave(OUTDIR + "sim_alineadas.png",cmap(sim))
io.imsave(OUTDIR + "shiftmap.png",cmap(shiftmat))

