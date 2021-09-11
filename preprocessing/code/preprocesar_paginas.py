#!/usr/bin/python3
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
from PIL import Image, ImageMorph, ImageOps
from skimage import morphology as morph
import denoising
#
# ---------------------------------------------------------------------------------------
#
def imwrite(fname, img):
    '''
    simple wrapper for writing images, in case I change the I/O package
    '''
    img.save(fname, compression="group4")
#
# ---------------------------------------------------------------------------------------
#
def imrot(img, angle):
    w, h = img.size
    return img.rotate(angle, resample=Image.NEAREST, expand=True, fillcolor=1)
#
# ---------------------------------------------------------------------------------------
#
def imread(fname):
    img = Image.open(fname)
    if fext.lower()[:3] != "tif":
        return img
    if not 274 in img.tag_v2:
        return img
    if img.tag_v2[274] == 8:  # regression bug in PILLOW for TIFF images
        img = imrot(img, -90)
    return img
#
# ---------------------------------------------------------------------------------------
#
def remove_large_areas(i,maxsize):
    '''
    Esto anda muy bien
    '''
    labels = morph.label(i,connectivity=2)
    labels = labels.ravel()
    ids,counts = np.unique(labels,return_counts=True)
    #
    # replace labels by the size of the areas
    #
    size_map = np.array([counts[j] for j in labels],dtype=np.int).reshape(i.shape)
    i2 = np.copy(i)
    i2[size_map > maxsize] = 0
    return i2

#
# ---------------------------------------------------------------------------------------
#
def convexify(I):
    I = I.convert('L')
    I2 = ImageOps.invert(I)
    # mild convexity
    convex_pat = [
            '4:(.1. 1.. .1.)->1',
    ]
    lut = ImageMorph.LutBuilder(patterns=convex_pat).build_lut()
    mop = ImageMorph.MorphOp(lut)
    changed,I2 = mop.apply(I2)
    while changed > 000:
        print('changed',changed)
        changed,I2 = mop.apply(I2)

    return ImageOps.invert(I2)
#
# ---------------------------------------------------------------------------------------
#
def denoise_counting(I):
    i = np.array(I)
    #i2,_ = counting_filter.counting_filter(i,radius=4,p=0.1,interleave=2)
    i2,_ = denoising.counting_filter(i,radius=4,p=0.05,interleave=2)
    return Image.fromarray(i2.astype(np.bool))
#
# ---------------------------------------------------------------------------------------
#
if __name__ == '__main__':
    #
    # command line arguments
    #
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", type=str, default="/luisa/alineadas",
                    help="path prefix  where to find prealigned files")
    ap.add_argument("--out-dir", type=str, default="preproc",
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
    ap.add_argument("--recreate", type=bool, default=True,
                    help="Re-create source images tree.")
    #
    # INICIALIZACION
    #
    args = vars(ap.parse_args())
    prefix    = args["prefix"]
    list_file = args["list"]
    output    = args["out_file"]
    outdir    = args["out_dir"]
    debugdir  = args["debug_dir"]
    recreate  = args["recreate"]

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
    #
    #

    #
    # procesar archivos
    #
    with open(list_file) as fl:
        #
        # inicializacion de memoria
        #
        nimage = 0
        t0 = time.time()
        nerr = 0
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
            #foutdir = os.path.join(outdir,reldir)
            foutdir = outdir

            if not os.path.exists(foutdir):
                os.makedirs(foutdir,exist_ok=True)
            output_fname = os.path.join(outdir,fname)
            print(f'#{nimage} input={input_fname} output={output_fname}')

            I = imread(input_fname)
            #I = I.resize((I.size[0]//2,I.size[1]//2))
            #I = I.rotate(2)
            #trim = max(I.size)*math.tan(math.pi*2/180) # maximum size of undefined border
            #trim = 50
            #
            # remove trim pixels from each side
            #
            #box = (trim,trim,I.size[0]-trim,I.size[1]-trim)
            #I = I.crop(box)
            #I = (1 - np.array(img)).astype(np.float)
            #I = transf.rescale(I,0.5,anti_aliasing=False)
            #print(np.max(I))
            #I = (1-np.array(img)).astype(np.bool)
            #plt.figure(1,figsize=(40,20))
            i  = (1-np.array(I)).astype(np.bool)
            #
            # estimate noise
            #
            #print('estimating noise level     ... ',end='')
            #t0 = time.time()
            #p0,p1 = denoising.estimate_noise(i,radius=10)
            #print('({0:6.3f}s)'.format(time.time()-t0))
            #
            # this is not really independent noise, and there is noise even when there are perfectly flat
            # regions.
            # therefore, we always consider a minimum error probability even if the estimate is otherwise
            #perr = max(0.05,max(p0,p1))
            print('denoising .................... ',end='')
            t0 = time.time()
            # parametros anteriores (buenos)
            #i2, _ = denoising.counting_filter(i, radius=4, p=perr, interleave=2, decay=False)
            # parametros con decay
            #i2, _ = denoising.counting_filter(i, radius=4, p=0.025, interleave=2, decay=True)
            # sin interleave
            i2, _ = denoising.counting_filter(i, radius=8, p=0.025, interleave=1, decay=True)
            print('({0:6.3f}s)'.format(time.time()-t0))

            print('removing large black areas ... ',end='')
            t0 = time.time()
            i3 = remove_large_areas(i2,7000)
            print('({0:6.3f}s)'.format(time.time()-t0))
            I3 = Image.fromarray((1-i3).astype(np.bool))

            #I2 = np.array(I)
            #plt.subplot(131)
            #plt.imshow(I)
            #plt.subplot(132)
            #plt.imshow(I2)
            #plt.subplot(133)
            #prof = np.sum(1-I2,axis=0)
            #profthres = (prof > 100)
            #plt.plot(prof)
            #plt.plot(profthres*200)
            #plt.show()
            imwrite(output_fname,I3)
            
        #
        # fin main
        #
# ---------------------------------------------------------------------------------------
