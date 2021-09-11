#!/usr/bin/python3 
# -*- coding: utf-8 -*-
#
# bibliotecas standard de Python
#
import os
import sys
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
#==============================================================================
#

def imwrite(fname,img):
    img.save(fname,compress="tiff_lzw")

#
#==============================================================================
#

def imrot(img,angle):
    w,h = img.size
    return img.rotate(angle, resample=Image.NEAREST,expand=True,fillcolor=1)

#
#==============================================================================
#
def imread(fname):
    _,ext = os.path.splitext(fname)
    ext = ext[1:].lower()
    img = Image.open(fname)
    if ext[:3] == 'tif':
        if not 274 in img.tag_v2:
            return img
        if img.tag_v2[274] == 8: # regression bug in PILLOW for TIFF images
            img = imrot(img,-90)
    return img

#
#==============================================================================
#
STRIPCHARS = '.-_;\'\",<>'
OUTDIR   = 'results'
EMPTYDIR = 'results/empty'

#==============================================================================

def resumir_bloque(hash_bloque):
    all_texts = db.queryExec(f"SELECT texto from texto where hashidbloque = '{hash_bloque}'").fetchall()
    textos = list()
    total = 0
    vacios = 0
    nolegibles = 0
    legibles = 0
    for txt_row in all_texts:
        txt = urllib.parse.unquote(txt_row[0])
        txt.strip()
        if len(txt) == 0:
            vacios += 1
        elif txt.find('@') >= 0:
            nolegibles += 1
        else:
            legibles += 1
            textos.append(txt)
        total += 1
    #
    # decisiones
    #
    if vacios == total:
        return " "
    elif legibles == 0:
        return "@"
    elif legibles < 3:
        bestidx = 0
    else:
        dist_mat = np.zeros((legibles, legibles))
        for i in range(legibles):
            for j in range(i):
                # a los efectos de calcular distancias, ignoramos puntitos y cosas asi, e ignoramos capitalizacion
                dist_mat[i, j] = txtdist.levenshtein(textos[i].strip(STRIPCHARS).lower(),
                                                     textos[j].strip(STRIPCHARS).lower())
                dist_mat[j, i] = dist_mat[i, j]
        bestidx = int(np.argmin(dist_mat, axis=0)[0])
    return textos[bestidx]

#==============================================================================

def resumir_fila(hash_hoja,fila):
    db.getConnection(port=config.DB_RPORT)

    query = f"SELECT max(i1),min(j0),max(j1) FROM bloque WHERE hashhoja='{hash_hoja}' AND i0={fila}"
    res = db.queryExec(query).fetchall()
    i0 = fila
    i1,j0,j1 = res[0]

    query = f"SELECT indice,hashid FROM bloque WHERE hashhoja='{hash_hoja}' AND i0={fila} ORDER BY indice"
    all_blocks = db.queryExec(query).fetchall()
    #print('\t\t\t fila', i0, i1, j0, j1, 'alto', i1 - i0, 'ancho', j1 - j0)
    texto_fila = ''
    for block_row in all_blocks:
        ind_bloque = block_row[0]
        hash_bloque = block_row[1]
        texto = resumir_bloque(hash_bloque)
        texto_fila += ' '
        texto_fila += texto
    return i0,i1,j0,j1,texto_fila

#==============================================================================

def resumir_hoja(hash_hoja,ruta_rollo):
    margin = 10
    db.getConnection(port=config.DB_RPORT)

    query = f"SELECT filename FROM hoja WHERE hash='{hash_hoja}'"
    cursor = db.queryExec(query)
    res = cursor.fetchone()
    ruta_hoja  = res[0]
    
    print('\thoja ',ruta_hoja)
    imgpath = os.path.join(config.ALIGNED_DIR,ruta_rollo,ruta_hoja + '.tif')
    
    img = imread(imgpath)

    query = f"SELECT DISTINCT i0 FROM bloque WHERE hashhoja='{hash_hoja}' ORDER BY i0"
    all_rows = db.queryExec(query).fetchall()

    ruta_hoja = ruta_hoja.replace('.','-')
    for b in all_rows:
        fila = b[0]
        #print(f'\t\t{fila}')
        i0,i1,j0,j1,texto = resumir_fila(hash_hoja,fila)
        width, height = img.size
        #print('\t\t\t texto',texto)
        outfile = f'{ruta_hoja}_rows_{i0:04d}-{i1:04d}'
        if i0 > margin:
            i0 -= margin
        if i1 < (height-margin):
            i1 += margin
        if j0 > margin:
            j0 -= margin
        if j1 < (width-margin):
            j1 += margin
        box  = (j0, i0, j1, i1)
        line = img.crop(box)
        if len(texto.strip()) == 0:
            imwrite(os.path.join(EMPTYDIR,outfile+'.tif'), line)
        else:
            with open(os.path.join(OUTDIR,outfile+'.txt'),'w') as ftxt:
                print(texto,file=ftxt)
            imwrite(os.path.join(OUTDIR,outfile+'.tif'), line)

#==============================================================================

def resumir_rollo(idrollo):
    
    db.getConnection(port=config.DB_RPORT)
    query = f"SELECT path FROM rollo WHERE id={idrollo}"
    res  = db.queryExec(query).fetchone()
    ruta_rollo = res[0]

    query = f"SELECT hash FROM hoja WHERE rollo={idrollo} ORDER BY id"
    cursor = db.queryExec(query)
    
    for row in cursor.fetchall():
        hash_hoja = row[0]
        resumir_hoja(hash_hoja,ruta_rollo)

#==============================================================================

def resumir_todo():
    query = f"SELECT id FROM rollo ORDER BY id"
    db.getConnection(port=config.DB_RPORT)
    cursor = db.queryExec(query)
    for row in cursor.fetchall():
        print('procesando rollo', row[0])
        resumir_rollo(row[0])

#==============================================================================

if __name__ == '__main__':
    dbconn = db.getConnection(port=config.DB_RPORT)
    os.makedirs(OUTDIR,exist_ok=True)
    os.makedirs(EMPTYDIR,exist_ok=True)
    if len(sys.argv) > 1:
        id_rollo = sys.argv[1]
        resumir_rollo(id_rollo)
    else:
        resumir_todo()

#==============================================================================
