#!/usr/bin/python3
# -*- coding:utf-8 -*-
import numpy as np

palabras = list()

PALABRAS='../compilados/palabras.txt'
NOMBRES='../compilados/nombres.txt'
OTRAS='../compilados/otras.txt'
M = 256

def valida(x):
    if not len(x):
        print("Aviso: palabra vacía.")
        return False
    for r in range(len(x)):
        i = ord(x[r-1])
        if i >= M:
            print(f"Aviso: caracter '{i}' no admisible en palabra '{x}'")
            return False
    return True

#
# leemos todas las palabras y nombres
# agregamos terminador '@' a cada lado 
#
for lista in (PALABRAS,NOMBRES,OTRAS):
    with open(lista,'r') as f:
        li = 0
        for p in f:
            if len(p.strip()) == 1:
                continue # ignoramos palabras de largo 1 en el armado de P()
            if valida(p.strip()):
                palabras.append(p.strip())
            else:
                print(f'Palabra inválida encontrada en {lista} en la linea {li}')
            li += 1

#
# armamos matriz de probabilidades condicionales
# Pr( x_{k}=j | x_{k-1}=i ) = P[i,j]
#
# usamos una pequeña normalizacion
e = (1/M)
P = e*np.ones((M,M))
for x in palabras:
    x = "@"+x+"@"
    for r in range(1,len(x)):
        i = ord(x[r-1])
        j = ord(x[r])
        P[i,j] += 1

#
# normalizamos conteos para obtener estimacion de probabilidades
#
for i in range(M):
    S = np.sum(P[i,:])
    P[i,:] *= (1.0/S)


#
# El score de una palabra es el promedio de la verosimilitud de todos sus caracteres
#
def wordscore(p,type='mean'):
    if type == 'mean':
        return wordscore_mean(p)
    elif type == 'worst':
        return wordscore_worst(p)


def wordscore_mean(p):
    if not valida(p):
        return None
    p = '@'+p+'@' # Princesa Leia
    n = len(p)
    l = 0
    for r in range(1,n):
        i = ord(p[r-1])
        j = ord(p[r])
        l += np.log2( P[ i, j ] )
    return l/n


def wordscore_worst(p):
    if not valida(p):
        return None
    p = '@'+p+'@' # Princesa Leia
    n = len(p)
    l = 0
    for r in range(1,n):
        i = ord(p[r-1])
        j = ord(p[r])
        lr = np.log2( P[ i, j ] )
        if lr < l:
            l = lr
    return l


if __name__ == "__main__":
    L = np.zeros(len(palabras))
    i = 0
    for p in palabras:
        L[i] = wordscore(p,type='mean')
        i += 1
    print('log-likelihood de palabras conocidas:')
    print('promedio:',np.mean(L))
    print('std.dev.:',np.std(L))
    print('minimo:',np.min(L), palabras[np.argmin(L)] )
    print('mediana:',np.median(L))
    print('maximo:',np.max(L), palabras[np.argmax(L)] )
    

