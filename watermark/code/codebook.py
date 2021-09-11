#!/usr/bin/python3
# -*- coding:utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import util
#
# cargamos datos de MNIST
#
print('Cargando')
X0 = np.loadtxt('/datos/mnist/train_images.asc')
t0 = np.loadtxt('/datos/mnist/train_labels.asc')

X1 = np.loadtxt('/datos/mnist/test_images.asc')
t1 = np.loadtxt('/datos/mnist/test_labels.asc')

#
# juntamos todo
#
print('Juntando')
X = np.concatenate((X0,X1),axis=0)*(1.0/256.0)
t = np.concatenate((t0,t1),axis=0)
#
# ordenamos por etiquetas
# 
N = 256
m = X.shape[1]
Z = list()
for d in range(10):
    which = (t == d)
    nd = np.sum(which)
    print("number of digits ",d,"is",nd)
    Xd = X[which,:]
    #Z.append( Xd )
    #
    # calculamos las distancias entre todas las muestras
    # de cada dígito
    #
    D = np.zeros(nd,nd) # D(x,y) = ||x-y||^2 = ||x||^2+ ||y||^2 - 2<x,y>
    x2 = np.sum(Xd**2,axis=1)
    D = D + np.outer(np.ones(nd),x2)
    D = D + np.outer(x2,np.ones(nd))
    D = D - 2*np.dot(Xd,Xd.T)
    #
    # permutamos la matriz según 
    # los que tengan la distancia mínima más grande
    #
    # buscamos las muestras con distancia mínima máxima 
    # evitamos contar la diagonal, que es todo 0
    sD = np.min(D + (np.max(D)+1)*np.eye(D.shape[0]),axis=1)
    idx = np.argsort(sD)
    idx = idx[-N:]
    print('min dist=',sD[idx[0]])
    D = D[idx,:]
    D = D[:,idx]
    #
    # ordenamos según distancia
    #
    idx = idx[-N:]
    Xd = Xd[idx,:]
    plt.figure()
    plt.imshow(D)
    plt.colorbar()
    plt.title(f'digit {d}')
    imk = util.dictionary_mosaic(Xd,2,0.2)
    plt.figure()
    plt.imshow(imk)
    np.savetxt(f'digit_{d}.txt',Xd,fmt='%7.5f')
plt.show()        
