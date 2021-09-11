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

#----------------   -----------------------------------------------------------------------

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
    # codificar mensaje
    #
    fecha = time.strftime("%Y-%m-%d %H:%M")
    mensaje = ("ORIG:\n" 
        "DIGITALIZADO por INEX en N2\n"
        "COPIA:\n"
        f"FECHA {fecha}\n"
        f"DEST {nombre}\n"
        f"DOC {cedula}\n"
        f"ORG {org}")
    print("\nMENSAJE ESCRITO:")
    print(mensaje)
    encoded_bytes = rsc.encode(mensaje)
    encoded_bytes_bytes = bytes(encoded_bytes,encoding="raw_unicode_escape")
    encoded_bytes = str(encoded_bytes_bytes,encoding="raw_unicode_escape")
    decoded_bytes, parity = rsc.decode(encoded_bytes)
    Isalida = Ientrada.copy()
    mask = 0x80
    for k in range(255*8):
        i = rows[k]
        j = cols[k]
        Isalida.putpixel((j,i), (encoded_bytes_bytes[int(k/8)] & mask != 0))
        mask = mask >> 1
        if mask == 0:
            mask = 0x80
    Isalida.save(salida)


#---------------------------------------------------------------------------------------
