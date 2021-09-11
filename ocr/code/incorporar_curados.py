#!/usr/bin/env python3
'''
Los archivos curados, por alguna razón que olvidé, quedaron a la mitad de tamaño, de 8 bits, y con pérdida
o algún artefacto generado por el reescalado.
El tema es que los archivos curados, además de tener el texto corregido y muestras malas borradas, tienen
versiones recortadas de las imágenes.

Pero lo ideal es usar las imagenes en B/N originales. 

Este script toma las imágenes originales de 1 bit en TIFF, las imágenes curadas, y genera una carpeta
nueva en donde están los textos y las imágenes curadas pero en 1 bit. Para esto no me queda otra que ir a buscar
la correspondiente en el conjunto original, teniendo en cuenta todos los desplazamientos posibles entre una y otra.



'''
import os
import sys

import numpy as np
import calamardo
from PIL import Image
import argparse
import random
import scipy.signal as dsp
import skimage.transform as trans

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("--origdir", type=str, required=True,
                    help="directory with original 1 bit tiff images")
    ap.add_argument("--curdir", type=str, required=True,
                    help="directory with curated dataset in 8 bit, downscaled images")
    ap.add_argument("--outdir", type=str, required=True,
                    help="output directory")

    args = vars(ap.parse_args())

    origdir    = args["origdir"]
    curdir     = args["curdir"]
    outdir     = args["outdir"]
    cur_img_files = [f for f in os.listdir(curdir) if os.path.isfile(os.path.join(curdir, f)) and f[-3:].lower() == 'tif' ]
    os.makedirs(outdir,exist_ok=True)

    for fname in cur_img_files:
        cur_img_file  = os.path.join(curdir,fname)
        orig_img_file = os.path.join(origdir,fname)
        out_img_file  = os.path.join(outdir,fname)
        print('curated=',cur_img_file,'orig=',orig_img_file,'out=',out_img_file)

        cur_img = np.array(Image.open(cur_img_file))
        orig_img = np.array(Image.open(orig_img_file))
        cur_height, cur_width = cur_img.shape
        orig_height,orig_width = orig_img.shape
        ratio = cur_height/orig_height
        down_width  = ratio*orig_img.shape[1]
        orig_img_down =  trans.resize(orig_img,(cur_height,down_width),anti_aliasing=True,preserve_range=True,order=1)
        if down_width == cur_width:
            print('no crop')
            Image.fromarray(orig_img).save(out_img_file)
        else:
            #
            # seek best alignment
            #
            G = dsp.correlate(orig_img_down, cur_img, method="fft", mode='same')
            linmax = np.argmax(np.abs(G))
            i = linmax // G.shape[1]
            j = linmax % G.shape[1]
            j0_down = j - cur_width // 2
            j1_down = j0_down + cur_width
            print('crop from ',j0_down,'to',j1_down)
            j0 = int(j0_down / ratio)
            j1 = int(j1_down / ratio)
            if j0 < 0 or j1 < 0 or j1 > orig_width:
                print('bad match')
                Image.fromarray(orig_img).save(out_img_file)
            else:
                print('crop from ',j0,'to',j1)
                orig_crop = orig_img[:,j0:j1]
                Image.fromarray(orig_crop).save(out_img_file)


