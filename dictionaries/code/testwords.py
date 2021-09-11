#!/usr/bin/python3 
#-*- coding: utf-8 -*-
import wordmodel
import matplotlib.pyplot as plt
import numpy as np

n = len(wordmodel.palabras)
L = np.zeros(n)
for i in range(n):
    L[i] = wordmodel.wordscore(wordmodel.palabras[i],type='worst')

badwords = list()
with open('../palabras/badwords.txt') as f:
    for p in f:
        if wordmodel.valida(p.strip()):
            badwords.append(p.strip())

Lbad = np.zeros(len(badwords))
for i in range(len(badwords)):
    Lbad[i] = wordmodel.wordscore(badwords[i],type='worst')

plt.figure()
plt.hist(L,100,color=(0,1,0,0.5))
plt.hist(Lbad,100,color=(1,0,0,0.5))
plt.grid(True)
plt.show()
