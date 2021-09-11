#!/usr/bin/python3
# -*- coding:utf-8 -*-

import os
import sys
import argparse
import numpy.random as random
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import util
from PIL import Image


#==============================================================================

DEFAULT_ROOTDIR = '/workspace/microfilm/0.orig_short/'
DEFAULT_OUTDIR  = './'
DEFAULT_DIGDIR  = "./digits/256"
DEFAULT_IMLIST  = "images.list"

#==============================================================================

def print_digits(im, codebook, text, number):
    used  = np.zeros((10,n))
    im = im.rotate(-90,expand=1)
    im = im.convert('L')
    N,M = im.size
    i0 = M - 200 - W
    j0 = N - 200 -8*W
    
    # number of available digits
    C = codebook.shape[1] 
    for k in range(len(text)):
        char  = ord(text[k])
        digit = int(number[k])
        offset  = char - ord('0')
        i     = i0 
        j     = j0+ k*W
        
        # avoid repeated digits!
        # shift the digit up until we find a spare one
        while used[digit,offset]:
            offset = np.mod(offset + 1,C)
        
        used[digit,offset] = 1 # mark as used
        imc = np.reshape(codebook[digit,offset,:],(w,w))
        imc = 255.0*(1-imc)
        imc = Image.fromarray(imc)
        imc = imc.resize((W,W),resample=Image.NEAREST)
        im.paste(imc,(j,i))
    
    im = im.convert('1',dither=0)
    return im

#==============================================================================

if __name__ == '__main__':
    
    epilog = "Output image file name is built from input name and parameters."
    parser = argparse.ArgumentParser(epilog=epilog)
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-r","--rootdir", help="root dir of image dataset", default=DEFAULT_ROOTDIR )
    parser.add_argument("-d","--outdir",  help="output directory", default=DEFAULT_OUTDIR )
    parser.add_argument("-D","--digdir", help="output directory", default=DEFAULT_DIGDIR )
    parser.add_argument("watermark", help="watermark text. Alphanumeric, no spaces or symbols")
    parser.add_argument("imagelist", help="list of images")
    args = parser.parse_args()

    cmd = " ".join(sys.argv)
    #print(("Command: " + cmd))
    #print(args)

    #-------------------------------------------------------------------------
    # load codebook of digits
    #-------------------------------------------------------------------------
        
    aux = np.loadtxt(f'{args.digdir}/digit_0.txt')
    n,m = aux.shape
    w = int(np.sqrt(m))
    #
    #size of letters
    #
    w = int(np.sqrt(m))
    W = w*4

    rng = random.default_rng(18636998)
    if len(args.watermark) != 8:
        print("AVISO: watermark debe tener exactamente 8 caracters")
        exit(1)

    codebook = np.empty((10,n,m))
    for d in range(10):
        codebook[d] = np.loadtxt(f'{args.digdir}/digit_{d}.txt')


    with open(args.imagelist) as image_list_file:

        image_list = [ im.strip() for im in image_list_file ]
        num_images = len(image_list)
        page_number = 1        

        for rel_image_path in image_list:
            print(f'Processing image {page_number:04d}/{num_images:04d}: {rel_image_path}')
            abs_image_path   = args.rootdir + rel_image_path
            rel_image_dir, _ = os.path.split(rel_image_path)
            out_image_path, _   = os.path.splitext(rel_image_path)
            out_image_path = out_image_path + '.tif'
            abs_outdir = f'{args.outdir}/{rel_image_dir}'

            im = Image.open(abs_image_path)

            if not os.path.exists(abs_outdir):
                os.mkdir(abs_outdir)

            number = f"{page_number:08d}"
            im = print_digits(im, codebook, args.watermark, number)
            im.save(out_image_path)
            
            page_number += 1

#==============================================================================
