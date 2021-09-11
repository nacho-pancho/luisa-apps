#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 12 17:22:41 FIRST_CROP18

@author: nacho
"""
import sys
import os
import time
import argparse

import numpy as np
from PIL import Image
from PIL import ImageMorph as morph
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import scipy.signal as dsp

import calamardo


# ---------------------------------------------------------------------------------------

ROW_ABS_THRES = 20  #
ROW_REL_THRES = 4  # 4 more pixels than local baseline
COL_ABS_THRES = 1  # column has at least three pixels black
COL_REL_THRES = 0.1  # the intensity of the column is less than 20% of the maximum
MIN_WORD_SEP = 20  # minimum separation between two words
MAX_LETTER_SEP = 18
BLOCK_ABS_THRES = 4  # minimum number of pixels in a valid line
TRAZO = 1.0
COLOR = (0.0, 0.2, 0.4, 0.1)
#COLORMAP = plt.get_cmap('cool')
COLORMAP = plt.get_cmap('gray')
WIN_SIZE = 1024
MIN_ROW_HEIGHT = 20  # smallest letter I found was about 23
MAX_ROW_HEIGHT = 50  # smallest letter I found was about 50
COMP='lzw'

# ---------------------------------------------------------------------------------------

def imwrite(fname, img):
    '''
    simple wrapper for writing images, in case I change the I/O package
    '''
    img.save(fname, compression=COMP)


# ---------------------------------------------------------------------------------------

def imrot(img, angle):
    w, h = img.size
    return img.rotate(angle, resample=Image.NEAREST, expand=True, fillcolor=1)


# ---------------------------------------------------------------------------------------

def imread(fname):
    img = Image.open(fname)
    if fext.lower()[:3] != "tif":
        return img
    if not 274 in img.tag_v2:
        return img
    if img.tag_v2[274] == 8:  # regression bug in PILLOW for TIFF images
        img = imrot(img, -90)
    return img

# ---------------------------------------------------------------------------------------

if __name__ == '__main__':
    #
    # command line arguments
    #
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", type=str, default="/luisa/alineadas",
                    help="path prefix  where to find prealigned files")
    ap.add_argument("--out-dir", type=str, default="",
		    help="if specified, save data to this output directory as images and text files")
    ap.add_argument("--out-file", type=str, default="",
                    help="if specified, save data to HDF5 with this file name.")
    ap.add_argument("--list", type=str, default="",
                    help="text file where input pre-aligned files are specified")
    ap.add_argument("--more-debug", action="store_true",
                    help="Save a LOT of debugging and diagnostic info (much slower!).")
    ap.add_argument("--debug-dir", type=str, default="",
                    help="Save debugging and diagnostic info to specified directory.")
    ap.add_argument("--force", action="store_true",
                    help="Forces the output to be overwritten even if it exists.")
    ap.add_argument("--margin", type=int, default=0,
                    help="Cut this number of pixels from each side of image before analysis.")
    #
    # INICIALIZACION
    #
    args = vars(ap.parse_args())
    prefix    = args["prefix"]
    list_file = args["list"]
    output    = args["out_file"]
    outdir    = args["out_dir"]
    debugdir  = args["debug_dir"]


    if not len(list_file):
        print('Debe especificar una lista de archivos.')
        exit(1)

    if not os.path.exists(list_file):
        print(f'Lista {list_file} no encontrada.')
        exit(1)

    if not os.path.exists(prefix):
        print(f'Directorio de origen {prefix} no encontrado.')
        exit(1)

    #
    # create HDF5 data file, if desired
    #
    save_hdf5 = len(output) > 0
    if save_hdf5:
        calamar = calamardo.CalamariFile(output)	
    else:
        calamar = None

    #
    # create plain files, if requested
    #    
    save_files = len(outdir) > 0
    if save_files:
        os.makedirs(outdir,exist_ok=True)

    if not save_files and not save_hdf5:
        print('Debe elegir al menos un tipo de salida (out-dir o out-file)')
        exit(1)
    
    save_debug = len(debugdir) > 0
    more_debug = False
    if save_debug:
        print(f"AVISO: modo depuracion; se generan archivos adicionales; más lento.")
        os.makedirs(debugdir,exist_ok=True)
        if args["more_debug"]:
            more_debug = True
            print(f"AVISO: EXTRA depuracion: se generan MUCHOS archivos adicionales; MUCHO más lento.")
    #
    # procesar archivos
    #
    with open(list_file) as fl:
        #
        # inicializacion de memoria
        #
        errors = list()
        nimage = 0
        nrows  = 0
        t0 = time.time()
        for relfname in fl:
            #
            # proxima imagen
            #
            nimage = nimage + 1
            #
            # ENTRADA Y SALIDA
            #
            # nombres de archivos de entrada y salida
            #
            relfname = relfname.rstrip('\n')
            reldir, fname = os.path.split(relfname)
            fbase, fext = os.path.splitext(fname)
            input_fname = os.path.join(prefix, relfname)

            print(f'#{nimage} input={input_fname}',end="")

            #
            # creamos carpeta de destino si no existe
            #
            fcsvrows = os.path.join(outdir,fbase + '.lines')
            if save_files:
                if os.path.exists(fcsvrows) and not args["force"]:
                    print('CACHED.')
                    continue
                if not os.path.exists(outdir):
                    os.makedirs(outdir)

            if not os.path.exists(input_fname):
                print("(input not found)")
                errors.append(input_fname)
                continue

            fpath = fname[:(fname.find('/') + 1)]
            #
            # read input image -- should be preprocessed!
            #
            try:
                img = imread(input_fname)
            except:
                print("(error reading image)")
                errors.append(input_fname)
                continue

            Iorig = 1 - np.array(img)
            #
            # scale to 1/2 for this analysis
            #
            scale = 2
            img = img.resize((img.size[0]//scale,img.size[1]//scale))
            #
            # convert to numpy and set 0 = background (it is stored the other way)
            #
            I = 1 - np.array(img)
            margin = args["margin"]
            if margin > 0:
                I = I[margin:-margin, margin:-margin]

            vprofile = np.mean(I,axis=1)
            hprofile = np.mean(I,axis=0)
            vprofile = vprofile * (1/ np.max(vprofile))
            hprofile = hprofile * (1/ np.max(hprofile))
            vvar = np.abs(np.diff(vprofile)) # compute difference (variation)
            hvar = np.abs(np.diff(hprofile)) # compute difference (variation)
            vscore = np.mean(vvar)
            hscore = np.mean(hvar)
            if vscore > hscore:
                orient = "*"
            else:
                orient = "."
            print(f"\tvscore={vscore:8.4f}\thscore={hscore:8.4f}\torient={orient}")               
        #
        # fin loop principal
        #
        if save_hdf5:
            calamar.close()

        if nimage > 0:
            meandt = (time.time() - t0) / nimage
            print(f'Average time per image: {meandt} seconds. ')
        print('Procesadas ',nrows, ' filas')
        nerr = len(errors)
        if nerr > 0:
            print(f'ERROR AL PROCESAR {nerr} ARCHIVOS:')
            for l in errors:
                print(l)
        else:
            print("completo.")
        #
        # fin main
        #
# ---------------------------------------------------------------------------------------
