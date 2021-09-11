#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 12 17:22:41 2018

@author: nacho
"""
#import os.path
import sys
import numpy as np
from PIL import Image,ImageMath
import os
import config
import scipy.signal as dsp
import time
import numpy.random as random
import unireedsolomon as rs
import datetime
import argparse
import time

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

    Ientrada = Image.open(entrada)
    mentrada = np.asarray(Ientrada)
    rng = random.default_rng(seed=19732019)
    #
    # generar 255 posiciones al azar en la imagen
    #
    img_width,img_height = Ientrada.size
    rows = rng.integers(img_height,size=255*8)
    cols = rng.integers(img_width,size=255*8)
    coords = set()
    for i in range(255*8):
        s = rows[i]*10000 + cols[i]    
        if s in coords:
            print("HORROR")
        else:
            coords.add(s)
    #
    # decodificar mensaje
    #
    mask = 0x80
    encoded_bytes = bytearray(255)
    for k in range(255*8):
        i = rows[k]
        j = cols[k]
        pix = mentrada[i,j] != 0
        if pix:
            encoded_bytes[int(k/8)] = encoded_bytes[int(k/8)]  | mask
        mask = mask >> 1
        if mask == 0:
            mask = 0x80
    encoded= str(encoded_bytes,encoding="raw_unicode_escape")
    decoded, parity = rsc.decode(encoded)
    print("MENSAJE LEIDO:\n"+decoded)


#---------------------------------------------------------------------------------------
