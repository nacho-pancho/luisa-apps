#!/usr/bin/python3 
#-*- coding: utf-8 -*-
import wordmodel
import matplotlib.pyplot as plt
import numpy as np

n = len(wordmodel.palabras)
L = np.zeros(n)
for i in range(n):
    L[i] = wordmodel.wordscore(wordmodel.palabras[i],type='worst')

todo = list()

with open('../compilados/palabras.txt') as f:
    for p in f:
        todo.append(p.strip())

with open('../compilados/nombres.txt') as f:
    for p in f:
        todo.append(p.strip())

todo = set(todo)

with open('../palabras/badwords.txt') as f:
    totales = 0
    presentes = 0
    raras = 0
    posibles = 0
    fp =  open('../results/posibles.txt','w')
    ff =  open('../results/filtradas.txt','w')
    for p in f:
        totales += 1
        p = p.strip()
        if p in todo:
            presentes += 1
            continue
        if wordmodel.valida(p):
            score1 = wordmodel.wordscore(p,type='worst')
            score2 = wordmodel.wordscore(p,type='mean')
            if (score1 > -10) and (score2 > -5):
                print(p,file=fp)
                posibles += 1
            else:
                print(p,file=ff)
                raras += 1
    fp.close()
    ff.close()
    print(f'Total:{totales} presentes:{presentes} raras:{raras} posibles:{posibles}')



