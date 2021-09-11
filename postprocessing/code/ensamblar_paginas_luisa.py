#!/usr/bin/python3 
# -*- coding: utf-8 -*-
#
# python-bottle ------- servidor web basado en Python, Bottle
# python-bottle-cork -- autenticacion y autorizacion basada en usuarios (FUNDAMENTAL para deploy!)
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
from PIL import Image, ImageDraw, ImageFont # procesamiento de imagenes
import distance as txtdist
import numpy as np
# 
# paquetes propios
#
import luisadbpg as db
#
#
#
STRIPCHARS = '.-_'
IMG_DIR = './data/img/novedadesCompleto/'
IMG_EXT = '.tif'
OUT_DIR = './data/out/'
db.connect()
cursor_hoja = db.queryExec("SELECT id,filename FROM hoja order by id")
for row_hoja in cursor_hoja.fetchall():
    id_hoja = row_hoja[0]
    fname_hoja = row_hoja[1]
    print('HOJA',id_hoja,'archivo',fname_hoja)
    orig = Image.open(IMG_DIR + fname_hoja + IMG_EXT)
    pag_orig = orig.convert(mode='RGB')
    cursor_bloque = db.queryExec("SELECT id,hash,i0,j0,i1,j1,idhoja FROM bloque WHERE idhoja={0:d} ORDER BY id".format(id_hoja))
    pag_trans = Image.new(mode='RGB',size=orig.size,color=(255,255,255))
    canvas = ImageDraw.Draw(pag_trans)
    for row_bloque in cursor_bloque.fetchall():
        id_bloque = row_bloque[0]
        hash_bloque = row_bloque[1]
        i0 = row_bloque[2]
        j0 = row_bloque[3]
        i1 = row_bloque[4]
        alto_renglon = i1 - i0
        textos_este_bloque = list()
        n = 0
        cursor_texto = db.queryExec("SELECT texto,idbloque from texto where idbloque = '" + hash_bloque + "'")
        for row_texto in cursor_texto.fetchall():
            txt =  urllib.parse.unquote(row_texto[0])
            txt.strip()
            textos_este_bloque.append(txt)
            n = n + 1
        if n == 0:
            continue
        dist_mat = np.zeros((n,n))
        for i in range(n):
            for j in range(i):
                # a los efectos de calcular distancias, ignoramos puntitos y cosas asi, e ignoramos capitalizacion
                dist_mat[i,j] = txtdist.levenshtein( textos_este_bloque[i].strip(STRIPCHARS).lower(), textos_este_bloque[j].strip(STRIPCHARS).lower() )
                dist_mat[j,i] = dist_mat[i,j]
        textos_identicos = np.max(dist_mat) == 0
        bestidx = int(np.argmin(dist_mat,axis=0)[0])
        linea = np.concatenate( (dist_mat[bestidx,:bestidx],dist_mat[bestidx,(bestidx+1):]) ) 
        if n > 1:
            meandist = np.mean(linea)
            meddist = np.median(linea)
            stddist = np.std(linea)
        else:
            meandist = 0
            meddist = 0
            stddist = 0
        mejor_texto = textos_este_bloque[bestidx]
        #print 'bloque',id_bloque,meddist,round(meandist,1),round(stddist,1),'\t\''+mejor_texto+'\''
        fnt = ImageFont.truetype('FreeMonoBold.ttf', max(12,alto_renglon-8))
        #fnt = ImageFont.truetype('DejaVuSerif-Bold.ttf', max(12,alto_renglon-8))
        # draw text, half opacity
        tono = int(min(255,meandist*10))
        canvas.text((j0,i0), mejor_texto, font=fnt, fill=(tono,0,0,255))
    #
    # mostramos de fondo la original
    #
    pag_blend = Image.blend(pag_orig,pag_trans,0.9)
    #pag_blend.show()
    pag_blend.save(OUT_DIR + fname_hoja + IMG_EXT)
