#!/usr/bin/python3
# -*- coding:utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import util
from PIL import Image
#
# cargamos datos de MNIST
#
IMGDIR='/workspace/microfilm/0.orig_short/r643/'
print('Cargando')
aux = np.loadtxt('digits/256/digit_0.txt')
n,m = aux.shape
w = int(np.sqrt(m))

im = Image.open(IMGDIR+'r643_0200.1975.tif')

codebook = np.empty((10,n,m))
for d in range(10):
    codebook[d] = np.loadtxt(f'digits/256/digit_{d}.txt')
im = im.rotate(-90,expand=1)
im = im.convert('L')
text = "HOLACOCO"
number = "00040125"
N,M = im.size
w = int(np.sqrt(m))
W = w*4
i0 = M - 200 - W
j0 = N - 200 -8*W
for k in range(len(text)):
    char  = ord(text[k])
    digit = int(number[k])
    offset  = char - ord('0')
    print('char',char,'off',offset)
    i     = i0 
    j     = j0+ k*W
    imc = np.reshape(codebook[digit,offset,:],(w,w))
    imc = 255.0*(1-imc)
    imc = Image.fromarray(imc)
    imc = imc.resize((W,W),resample=Image.NEAREST)
    im.paste(imc,(j,i))

plt.figure()
im = im.convert('1',dither=0)
im.save('test.tif')
plt.imshow(im,cmap=cm.gray)
plt.show()
