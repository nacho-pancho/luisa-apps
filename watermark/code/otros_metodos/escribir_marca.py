#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# requiere libtiff-tools (tiffset)
#
"""
Created on Wed Sep 12 17:22:41 2018

@author: nacho
"""
#import os.path
import sys
import numpy as np
from PIL import Image,ImageMath,ImageFilter
import os
import random as rng
import unireedsolomon as rs
import datetime
import argparse
import time

#---------------------------------------------------------------------------------------

def imwrite(fname,img):
    img.save(fname,compress="tiff_lzw")

#---------------------------------------------------------------------------------------

def imrot(img,angle):
    w,h = img.size
    #center = (int(w/2),int(h/2))
    return img.rotate(angle, resample=Image.NEAREST,expand=True,fillcolor=1)

#---------------------------------------------------------------------------------------

def imread(fname):
    img = Image.open(fname)
    if not 274 in img.tag_v2:
        return img
    if img.tag_v2[274] == 8: # regression bug in PILLOW for TIFF images
        img = imrot(img,-90)
    return img

#---------------------------------------------------------------------------------------
#
# mensaje insertado en pixeles al azar
#
def embed_random(img,msg):
    rng.seed(19732019)
    rsc = rs.RSCoder(255,208)
    encoded_msg = rsc.encode(msg)
    encoded_msg_bytes = bytes(encoded_msg,encoding="raw_unicode_escape")
    coords = set()
    mask = 0x80
    nbits = 255*8
    w,h = img.size
    c = len(img.getbands())
    if c == 1:
        band = img
    else:
        bands = img.split()
        band = img.getchannel(1)
    for k in range(nbits):
        row = rng.randint(0,h-1)
        col = rng.randint(0,w-1)
        s = (row<<16) + col    
        while s in coords:
            row = rng.randint(0,h-1)
            col  = rng.randint(0,w-1)
            s = (row<<16) + col    
        coords.add(s)
        x = band.getpixel((col,row)) & 254
        if (encoded_msg_bytes[int(k/8)] & mask) != 0:
            band.putpixel((col,row), x | 1)
        else:
            band.putpixel((col,row), x)
        mask = mask >> 1
        if mask == 0:
            mask = 0x80
    if c > 1:
        img = Image.merge(img.mode,(bands[0],band,bands[2]))
    else:
        img = band
    return img
#    
#---------------------------------------------------------------------------------------
#   
# mensaje insertado como marca de agua
#
def embed_watermark(img,msg):
    # 
    #
    # info de la imagen
    imw,imh = img.size  
    #
    # marca obviamente visible, como 'honeypot'
    #
    watermark = Image.new(mode='L', size=img.size,color=(0))
    canvas = ImageDraw.Draw(watermark)
    fnt = ImageFont.truetype('./FreeMonoBold.ttf', 64)

    canvas.text((50,25),msg,font=fnt, fill=(15) )
    #
    # marca de agua mucho más difícil de ver
    #
    fnt = ImageFont.truetype('./FreeMonoBold.ttf', 120)
    split_msg = msg.split('\n')
    tw,th = fnt.getsize(split_msg[0])
    msgh = th*len(split_msg)
    # get a drawing context
    imgc = len(img.getbands())
    for ty in range(300,imh,int(0.90*msgh)):
        canvas.text((300,ty), msg, font=fnt, fill=(1))
    #
    # modificar cada banda
    #
    if imgc == 1:
        img = ImageMath.eval("(A & 254) ^ B",A=img,B=watermark).convert('L')
    else:
        bands = img.split()
        b2 = list()
        for b in bands:
            b = ImageMath.eval("(A & 254) ^ B",A=b,B=watermark).convert('L')
            b2.append(b)
        img = Image.merge(img.mode,tuple(b2))
    return img

#--------------------------------------------------------------------------------------

from PIL import Image, ImageDraw, ImageFont

if __name__ == '__main__':
    #
    # procesamiento de linea de comandos usando argparse
    #
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--cedula", required=True,
        help="documento del destinatario")
    ap.add_argument("-n", "--nombre", required=True, 
        help="nombre del destinatario")
    ap.add_argument("-o", "--org", required=True,
        help="organización del destinatario")
    ap.add_argument("entrada", help="imagen de entrada")
    ap.add_argument("salida", help="imagen de salida")
    args = vars(ap.parse_args())

    nombre = args['nombre']
    cedula = args['cedula']
    org = args['org']
    entrada = args['entrada']
    salida = args['salida']
    
    img = imread(entrada)
    #
    # se genera un mensaje y se inserta de tres maneras en el texto:
    #
    # 1) en la metadata de la imagen TIFF
    # 2) en los LSB de un conjunto de 255 muestras al azar en la imagen
    # 3) como una marca de agua repetida en el fondo
    #
    img_width,img_height = img.size
    #
    # generar mensaje
    #
    fecha = time.strftime("%Y:%m:%d %H:%M")
    msg = ("ORIGINAL DIGITALIZADO por INEX en N2\n"
        f"COPIA CON FECHA {fecha}\n"
        f"DEST {nombre}\n"
        f"DOC {cedula}\n"
        f"ORG {org}")
    print("\nMENSAJE ESCRITO:")
    print(msg)
    #
    # las copias siempre serán o bien escala de grises o bien RGB
    # si la entrada es binaria, se convierte a 8 bits ('L')
    if img.mode == '1': 
        img = img.convert('L')
    #
    # blur para evitar ruido en JPG
    #
    #img = img.filter(ImageFilter.SMOOTH)
    #
    # embedding 2: como marca de agua
    #
    img = embed_watermark(img,msg)
    #
    # embedding 1: en pixeles individuales
    #
    img = embed_random(img,msg)
    
    imwrite(salida,img)
    # 270 es el tag 'ImageDescription'
    #user_comment = "UNICODE "+msg
    #os.system(f'tiffset -s 270 "{msg}" {salida}')
    # este es el tag EXIF de Tiff. Hay que ver como construirlo y pasarselo a tiffset.
    # no se si se puede.
    #os.system(f'tiffset -s 34665 "{exif}" {salida}')
    
