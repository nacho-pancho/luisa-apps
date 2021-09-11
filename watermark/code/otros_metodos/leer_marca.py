#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 12 17:22:41 2018

@author: nacho
"""
#import os.path
import sys
import os
import numpy as np
from PIL import Image,ImageMath
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
    _,ext = os.path.splitext(fname)
    ext = ext[1:].lower()
    img = Image.open(fname)
    if ext[:3] == 'tif':
        if not 274 in img.tag_v2:
            return img
        if img.tag_v2[274] == 8: # regression bug in PILLOW for TIFF images
            img = imrot(img,-90)
    return img

#---------------------------------------------------------------------------------------

def decode_random(img):
    w,h = img.size
    #
    # inicializar RNG
    #
    rng.seed(19732019)
    rsc = rs.RSCoder(255,208)
    #
    # generar 255 posiciones al azar en la imagen
    #
    #
    # decodificar mensaje RS
    #
    mask = 0x80
    encoded_bytes = bytearray(255)
    nbits = 255*8
    coords = set()
    if len(img.getbands()) > 1:
        band = img.getchannel(1)
    else:
        band = img 
    for k in range(nbits):
        row = rng.randint(0,h-1)
        col = rng.randint(0,w-1)
        s = (row<<16) + col    
        while s in coords:
            row = rng.randint(0,h-1)
            col  = rng.randint(0,w-1)
            s = (row<<16) + col
        coords.add(s)
        pix = band.getpixel((col,row)) & 1 
        if pix:
            encoded_bytes[int(k/8)] = encoded_bytes[int(k/8)]  | mask
        mask = mask >> 1
        if mask == 0:
            mask = 0x80
    encoded= str(encoded_bytes,encoding="raw_unicode_escape")
    try:
        decoded, parity = rsc.decode(encoded)
        return decoded
    except:
        return "(decoding error)"

#---------------------------------------------------------------------------------------

if __name__ == '__main__':
    #
    # procesamiento de linea de comandos usando argparse
    #
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada", help="imagen de entrada")
    args = vars(ap.parse_args())

    entrada = args['entrada']
    
    rsc = rs.RSCoder(255,208)

    img = imread(entrada)
    decoded = decode_random(img)
    print("MENSAJE LEIDO:\n"+decoded)
    #
    # revelar watermark de imagen
    #
    if len(img.getbands()) > 1:
        img = img.getchannel(1)
        img = ImageMath.eval("(A & 1)*255",A=img).convert('L')
        imwrite("watercolor.tif",img)
    else:
        img = ImageMath.eval("(A & 1)*255",A=img).convert('L')
        imwrite("watermark.tif",img)

#---------------------------------------------------------------------------------------
