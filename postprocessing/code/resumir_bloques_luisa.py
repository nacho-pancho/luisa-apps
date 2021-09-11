#!/usr/bin/python3 
# -*- coding: utf-8 -*-
#
# bibliotecas standard de Python
#
import os
import sys
import io
import time
import urllib.request, urllib.parse, urllib.error
#
#
#
import matplotlib.pyplot as plt  # ploteo
from PIL import Image, ImageDraw # procesamiento de imagenes
import distance as txtdist # distancia entre textos; pip install Distance
import numpy as np
# 
# paquetes propios
#
import config
import luisadbpg2 as db
#
#
#

def analizar(hoja=None):
    #
    # usamos una conexión especial
    #
    db.getConnection(dbname='tanda_0',port=config.DB_RPORT)

    num_por_bloque = list()
    num_textos_por_bloque = list()
    textos_por_bloque = list()
    arroba_total_por_bloque = list()
    arroba_parcial_por_bloque = list()
    vacios_por_bloque = list()
    iguales_por_bloque = list()
    distancias_entre_textos = list()
    dist_media_a_mejor = list()
    mejor_texto_por_bloque = list()
    bloque_totalmente_vacio = list()
    STRIPCHARS = '.-_;\'\",'
    print("id\ttotal\tvacios\t@total\t@parc\tmed\tmean\tstd\tiguales\ti3\ttexto")
    if hoja is None:
        query = "SELECT id,hash,i0,j0,i1,j1 FROM bloque ORDER BY id"
    else:
        subquery = f"SELECT id from hoja WHERE filename LIKE '%{hoja}%'"
        print(subquery)
        res = db.queryExec(subquery).fetchone()
        if res == None:
            print(f'ERROR: No hay ninguna hoja cuyo nombre se parezca a {hoja}')
            return
        idhoja = res[0]
        query = f"SELECT id,hash,i0,j0,i1,j1 FROM bloque WHERE idhoja={idhoja} ORDER BY id"
    all_blocks = db.queryExec(query).fetchall()

    for block_row in all_blocks:
        id_bloque = block_row[0]
        hash_bloque = block_row[1]
        textos_este_bloque = list()
        vacios = 0
        arrobas_totales = 0
        arrobas_parciales = 0
        nt = 0
        n = 0
        all_texts = db.queryExec(f"SELECT texto,idbloque from texto where idbloque = '{hash_bloque}'").fetchall()
        for txt_row in all_texts:
            txt =  urllib.parse.unquote(txt_row[0])
            txt.strip()
            nt = nt + 1
            if len(txt) == 0:
                vacios = vacios + 1
            elif txt == '@':
                arrobas_totales = arrobas_totales + 1
            elif txt.find('@') >= 0:
                arrobas_parciales = arrobas_parciales + 1
            textos_este_bloque.append(txt)
            n = n + 1
        if n < 3:
            continue
        bloque_totalmente_vacio.append(vacios + arrobas_totales == n)
        dist_mat = np.zeros((n,n))
        for i in range(n):
            for j in range(i):
                # a los efectos de calcular distancias, ignoramos puntitos y cosas asi, e ignoramos capitalizacion
                dist_mat[i,j] = txtdist.levenshtein( textos_este_bloque[i].strip(STRIPCHARS).lower(), textos_este_bloque[j].strip(STRIPCHARS).lower() )
                dist_mat[j,i] = dist_mat[i,j]
        bestidx = int(np.argmin(dist_mat,axis=0)[0])
        linea = np.concatenate( (dist_mat[bestidx,:bestidx],dist_mat[bestidx,(bestidx+1):]) ) 
        meandist = np.mean(linea)
        iguales = np.sum(linea == 0)
        meddist = np.median(linea)
        stddist = np.std(linea)
        mejor_texto = textos_este_bloque[bestidx]
        num_textos_por_bloque.append(n)
        textos_por_bloque.append(textos_este_bloque)
        arroba_parcial_por_bloque.append( arrobas_parciales )
        arroba_total_por_bloque.append( arrobas_totales )
        vacios_por_bloque.append( vacios )
        iguales_por_bloque.append( iguales )
        mejor_texto_por_bloque.append( mejor_texto)
        dist_media_a_mejor.append(meandist)
        distancias_entre_textos.append(dist_mat)
        rmed = round(meandist,1)
        rstd = round(stddist,1)
        pig = int(100*iguales/n)
        i3 = iguales >= 3
        print(f"{id_bloque}\t{nt}\t{vacios}\t{arrobas_totales}\t{arrobas_parciales}\t{rmed}\t{rstd}\t{iguales}\t{pig}\t{i3}\t\'{mejor_texto}\'")
    print('Porcentaje de bloques totalmente vacios: ', round( 100.0*np.sum(bloque_totalmente_vacio)/len(bloque_totalmente_vacio), 0)) 
    np.savez_compressed('num_por_bloque', num_por_bloque )
    np.savez_compressed('num_textos_por_bloque', num_textos_por_bloque )
    np.savez_compressed('textos_por_bloque', textos_por_bloque )
    np.savez_compressed('arroba_total_por_bloque', arroba_total_por_bloque )
    np.savez_compressed('arroba_parcial_por_bloque', arroba_parcial_por_bloque )
    np.savez_compressed('vacios_por_bloque',vacios_por_bloque )
    np.savez_compressed('iguales_por_bloque', iguales_por_bloque )
    np.savez_compressed('distancias_entre_textos',distancias_entre_textos )
    np.savez_compressed('dist_media_a_mejor', dist_media_a_mejor )
    np.savez_compressed('mejor_texto_por_bloque', mejor_texto_por_bloque )
    np.savez_compressed('bloque_totalmente_vacio', bloque_totalmente_vacio )

    bin_edges = list(range(30))
    plt.figure(1,figsize=(30,20))
    plt.hist(dist_media_a_mejor,bin_edges)
    plt.savefig('mdist.png',dpi=150)

    plt.figure(2,figsize=(30,20))
    plt.hist(num_textos_por_bloque,bin_edges)
    plt.savefig('num.png',dpi=150)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        fname_hoja = sys.argv[1]
        analizar(fname_hoja)
    else:
        analizar()
