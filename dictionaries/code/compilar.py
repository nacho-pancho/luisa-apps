#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# La idea de este script es generar dos archivos, uno de items propios y siglas,
# y otro de palabras comunes, a partir de todas las listas que hay en este proyecto.
#
import codecs

def compilar_lista(nombre_lista):
    items = list()
    with open(f'../{nombre_lista}.list','r') as fl:
        archivos = [a.strip() for a in fl]
    
        items = list()
        for arch in archivos:
            print(f'Tomando palabras de {arch:40s} ...',end='')
            with open('../'+arch,'r') as fa:
                palabras = [ p.strip() for p in fa ]
                lp = len(palabras)
                print(f' ( {lp:5d} )')
                items.extend(palabras)
    ln = len(items)
    print(f'Leidas: {ln} palabras.') 
    items = list(set(items))
    ln = len(items)
    print(f'Filtradas {ln} palabras distintas.') 
    
    print('Ordenando alfabéticamente')
    items.sort()
    with open(f'../compilados/{nombre_lista}.txt','w') as fo:
        for n in items:
            fo.write(n+'\n')

if __name__ == '__main__':
    compilar_lista('nombres')
    compilar_lista('palabras')
    compilar_lista('otras')
