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

def detect_bands(rmt, min_size):
    '''
    given a sequence of values, detects contiguous segments or 'bands' which are significantly
    darker than their neighborhood.
    '''
    # mark positions of up and down flanks
    dif = np.int8(rmt[1:]) - np.int8(rmt[:-1])
    upidx = np.flatnonzero(dif > 0) + 1
    dnidx = np.flatnonzero(dif < 0) + 1

    # no up transitions
    if len(upidx) == 0:
        upidx = list()
        upidx.append(0)

    # no down transitions 
    if len(dnidx) == 0:
        dnidx = list()
        dnidx.append(len(rmt))

    # if first flank is down, assume there is an up flank at 0
    if (len(dnidx) > 1) & (dnidx[0] < upidx[0]):
        upidx = np.insert(upidx, 0, 0)

    # more ups than downs means
    if len(upidx) > len(dnidx):
        dnidx = np.insert(dnidx, len(dnidx), len(rmt))

    bands = list(zip(upidx, dnidx))
    return bands


# ---------------------------------------------------------------------------------------

def detect_rows(img, debugdir):
    #
    # remove margins from both sides, only for the purpose of
    # this analysis
    #
    w = img.shape[1]
    row_sum = np.sum(img, axis=1)

    # parameters of order filter
    radius = 25
    domain = np.arange(-radius, radius + 1)
    order = int((radius * 2 + 1) / 3)
    order = 1
    row_sum_filtered = dsp.order_filter(row_sum, domain, order)
    row_sum_thresholded = (row_sum > ROW_ABS_THRES) & ((row_sum - row_sum_filtered) > ROW_REL_THRES)  #
    band_list = detect_bands(row_sum_thresholded, MIN_ROW_HEIGHT)
    row_list = [(r[0],r[1],0,w) for r in band_list]
    return row_list


# ---------------------------------------------------------------------------------------

def create_row_map(img, row_list, row_labels=None):
    band_map = img.astype(float)
    h,w  = band_map.shape
    for row in row_list:
        y0, y1,x0, x1 = row
        band_map[y0:y1, x0:x1] *= 0.7
    return band_map

# ---------------------------------------------------------------------------------------
def refine_rows(img, row_list):
    '''
    refine raw rows
    we apply a very conservative refinement which consists of some trimming from the sides
    and basic tests to rule out flukes like mostly solid or empty lines
    '''
    refined_row_list = list()
    #
    # reference value for trimming is average intensity on the middle third
    # of the band profile
    #
    for r in row_list:
        i0,i1,j0,j1 = r
        rh = i1-i0
        rw = j1-j0
        if rh < 10 or rw < 40: # too small
            continue        
        #
        # extract untrimmed row from image, adding a little slack above and below
        #
        #slack = 10
        #if i0 > slack:
        #    i0 -= slack
        #if i1 < (img.shape[1] - slack):
        #    i1 += slack
        band = img[i0:i1,:]
        #
        # horizontal profile of row
        #
        p = np.mean(band)
        if p < 0.02 or p > 0.98: # too full or too empty
            continue
        hp  = np.mean(band,axis=0)        
        #
        # trim white/black tails. 
        # a column is "white" if 90% or more of its pixels are 1
        # a column is "black" if 10% or less of its pixels are 0
        hpt = (hp >= 0.2) * (hp <= 0.8)
        hptf = dsp.order_filter(hpt,np.ones(41),35)
        nz = np.flatnonzero(hptf)
        if len(nz) >= 2:
            j0 = nz[0]
            j1 = nz[-1]
        else:
            # discard this line
            continue        
        refined_row_list.append((i0,i1,j0,j1))
    return refined_row_list


MAX_SAMPLES = 10000000
INI_SAMPLES = 10000

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
    ap.add_argument("--padding", type=int, default=10,
                    help="Add this number of pixelsto each side of the segmented line.")
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

            print(f'#{nimage} input={input_fname}')

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

            if more_debug:
                moredebugdir = os.path.join(outdir, fbase + '_debug')
                if not os.path.exists(moredebugdir):
                    os.makedirs(moredebugdir)
            else:
                moredebugdir = None
            if not os.path.exists(input_fname):
                print("(input not found)")
                errors.append(input_fname)
                continue

            fpath = fname[:(fname.find('/') + 1)]
            #
            # read input image -- should be preprocessed!
            #
            img = imread(input_fname)
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
            #
            # deteccion de bandas primaria
            #
            row_list = detect_rows(I, moredebugdir)
            #
            # refinamiento
            #
            refined_row_list = refine_rows(I,row_list)
            #
            # save debug info
            #
            if save_debug:
                row_labels = ["tall"] * len(row_list)
                row_map = create_row_map(np.array(img,dtype=float), row_list, row_labels)
                row_file = os.path.join(debugdir, fbase + "_raw_rows.jpg")
                plt.imsave(row_file, row_map,cmap=COLORMAP)

                row_labels = ["good"] * len(refined_row_list)                
                row_map_2 = create_row_map(np.array(img,dtype=float), refined_row_list, row_labels)
                row_file_2 = os.path.join(debugdir, fbase + "_refined_rows.jpg")
                plt.imsave(row_file_2, row_map_2,cmap=COLORMAP)
            #
            # guardar datos en HDF5
            #
            nrows,ncols = Iorig.shape
            pad = args["padding"]
            if save_hdf5:         
                for row in refined_row_list:
                    i0, i1, j0, j1 = row
                    i0, i1, j0, j1 = i0*scale, i1*scale, j0*scale, j1*scale
                    i0 = max(0,i0-pad)
                    i1 = min(nrows,i1+pad)
                    j0 = max(0,j0-pad)
                    j1 = min(ncols,j1+pad)                    
                    row_img = Iorig[i0:i1, j0:j1].astype(np.uint8)
                    if np.prod(row_img.shape) == 0:
                        print('warning: empty row: ',Iorig.shape,i0,i1,j0,j1)
                        continue
                    #
                    # de-scale!
                    #
                    calamar.write(row_img,"")
            #
            # guardar en archivos planos
            #
            if save_files:
                frows = open(fcsvrows,'w')
                for line in refined_row_list:
                    i0, i1, j0, j1 = line
                    i0, i1, j0, j1 = i0*scale, i1*scale, j0*scale, j1*scale
                    i0 = max(0,i0-pad)
                    i1 = min(nrows,i1+pad)
                    j0 = max(0,j0-pad)
                    j1 = min(ncols,j1+pad)
                    row_img = Iorig[i0:i1, j0:j1].astype(np.uint8)
                    if np.prod(row_img.shape) == 0:
                        print('warning: empty row!')
                        continue
                    print(f"{i0}\t{j0}\t{i1}\t{j1}", file=frows)
                    flineimg = os.path.join(outdir,f'{fbase}_rows_{i0:04d}-{j0:04d}-{i1:04d}-{j1:04d}.tif')
                    img = Image.fromarray((255*(1-row_img)).astype(np.uint8))
                    imwrite(flineimg,img)
                frows.close()
               
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
