#!/usr/bin/python3
# -*- coding:utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import scipy.signal as dsp
import util
from PIL import Image
#
# cargamos datos de MNIST
#
#
# CODEBOOK
#
# el codebook contiene n variantes
# de cada uno de los dígitos del 0 al 9
#
# cargamos el codebook de 0 para adivinar las dimensiones

aux = np.loadtxt('digits/256/digit_0.txt')
n,m = aux.shape
w = int(np.sqrt(m))
#
# el codebook para cada digito esta almacenado en un archivo
# llamado digit_d.txt donde d es 0,1,2...,9
#
codebook = np.empty((10,n,m))
for d in range(10):
    codebook[d] = np.loadtxt(f'digits/256/digit_{d}.txt')
#
# simbolos del codebook pasan de vectores d elargo m a
# imagenes de wxw
#
codebook = np.reshape(codebook,(10,n,w,w))
#
# imagen a procesar
#
im = Image.open('test_quart.jpg')
N, M = im.size
#
# si esta apaisada, rotar
#
if N > M:
    im = im.rotate(-90,expand=1)
    aux = M
    M = N
    N = aux
#
# intentamos adivinar si la imagen fue reescalada
# a grosso modo comparando la dimension mas grande
# con la dimensión típica de las imágenes originales
#
# 4 es la escala original, porque en la escala original
# las imagenes del codebook estan agrandadas x4
#
approx_scale = np.round(4*M/4900,1)
print('approx scale=',approx_scale)
#
# asumimos que alguien podría recortar los márgenes de
# la imagen, pero que nadie le agregaría margen
# entonces podemos concentrarnos en la zona
# en donde pusimos la marca en la imagen original
#
sw = approx_scale
x0 = N - sw*(50 + 8*w)
x1 = N
y0 = M - sw*(50 + w)
y1 = M

print(x0,y0,x1,y1)
im = im.crop((x0,y0,x1,y1))
im = im.convert('L')

I = np.asarray(im)*(1.0/255.0)
M,N = I.shape

I = 1- I
print('<I>=',np.mean(I))
#
# busqueda exhaustiva del primer 0
#
# los ceros siempre siguen una misma secuencia

best_scale = approx_scale
best_offset = 0
best_score = 0
best_char = '?'
best_imc = []
best_G = []

offset1  = ord('o') - ord('h')
offset2  = ord('l') - ord('h')
cmin = ord('0')
cmax = ord('Z')
CS   = cmax - cmin
best_i = -1
best_j = -1

print('Num. simbolos disponibles:',CS)
for c in range(CS):
    # los primeros tres ceros corresponden
    # partir de un cierto offset al azar
    # (en esta prueba no es al azar, sino 'h'
    # el segundo es 'o' y el tercero 'l')
    #
    c0 = np.mod(c,CS)
    c1 = np.mod(c+offset1,CS)
    c2 = np.mod(c+offset2,CS)

    #im0 = np.reshape(codebook[0,c0,:],(w,w))
    #im1 = np.reshape(codebook[0,c1,:],(w,w))
    #im2 = np.reshape(codebook[0,c2,:],(w,w))
    im0 = codebook[0,c0,:,:]
    im1 = codebook[0,c1,:,:]
    im2 = codebook[0,c2,:,:]

    imc = np.concatenate((im0,im1,im2),axis=1)

    imc = np.kron(imc,np.ones((int(approx_scale),int(approx_scale))))
    imc = np.fliplr(np.flipud(imc))
    imc = imc - np.mean(imc)
    imc = imc*(1.0/np.sqrt(np.sum(imc**2)))
    G = dsp.fftconvolve(I,imc,mode='same')
    limax = np.argmax(G)
    imax = int(limax/N)
    jmax = np.mod(limax,N)
    score = G[imax,jmax]
    offchar = chr(c+ord('0'))
    score = int(np.round(score))
    print(f'offset ord {c} char {offchar} {score} row {imax} col {jmax} score {score} best score {best_score} off {best_offset} chr {best_char}')
    
    if score > best_score:
        best_score = score
        best_offset = c
        best_char = offchar
        best_i = imax
        best_j = jmax
        dh,dw = imc.shape
        G[imax,jmax] = 10*score
        G[imax:(imax+dh),jmax:(jmax+dw)] += imc
        best_imc = np.copy(imc)
        best_G = np.copy(G)

print(f'offset ord {c} char {offchar} {score} row {imax} col {jmax} score {score} best score {best_score} off {best_offset} chr {best_char}')
plt.figure(1)
plt.imshow(I)
plt.figure(2)
best_G[best_i,best_j] = 2*np.max(best_G)
plt.imshow(best_G)
plt.figure(3)
plt.imshow(best_imc)
plt.show()
    

# for char0 in range(CS):
#     im0 = np.reshape(codebook[0,char0,:],(w,w))
#     for char1 in range(CS):
#         im1 = np.reshape(codebook[0,char1,:],(w,w))
#         for char2 in range(CS):
#             im2 = np.reshape(codebook[0,char2,:],(w,w))
#             imc = np.concatenate((im0,im1,im2),axis=1)
#             print(imc.shape)
#             W    = w*escala
#             i0   = M - 200 - W
#             j0   = N - 200 - 8*W
#             plt.figure()
#             plt.imshow(imc)
#             plt.show()
#             #imm = im.crop(())

