#!/usr/bin/env python3
import os
import sys

import numpy as np
import calamardo
from PIL import Image
import argparse
import random

def list_to_hdf5(cfout,indir,imglist):
    invalid = 0
    nimg = len(imglist)
    for i,f in enumerate(imglist):
        imgfname = os.path.join(indir,f)
        txtfname = os.path.join(indir,f[:-3]+'gt.txt')
        img   = Image.open(imgfname)
        I8    = np.array(img,dtype=np.uint8)
        if len(I8.shape)>2:
            if I8.shape[2] == 2:
                print('WARNING: alpha channel??!',imgfname,I8.shape)
                I8 = I8[:,:,0]
            elif I8.shape[2] >= 3:
                print('WARNING: RGB??',imgfname,I8.shape)
                I8 = I8[:,:,1] # green channel
                invalid += 1
                continue
        try:
            with open(txtfname,'r') as f:
                txt = f.readline().strip()
                if cfout.write(I8,txt) != 0:
                    invalid += 1
        except UnicodeDecodeError as e:
            print('ERROR: invalid UTF-8 text file!',txtfname)
            invalid += 1
            continue
        if i > 0 and not i % 100:
            print(f'{i:08d}/{nimg:08d}')
    print('total',nimg,'valid',nimg-invalid,'invalid',invalid)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("--indir", type=str, required=True,
                    help="base where files are stored")
    ap.add_argument("--outdir", type=str, required=True,
                    help="if specified, save HDF5 files to directory")
    ap.add_argument("--list", type=str, required=True,
                    help="list of files to process")
    ap.add_argument("--prefix", type=str, default="calamari",
                    help="output prefix file name")
    ap.add_argument("--val-ratio", type=float,
                    default=0.2,
                    help="fraction of input files reserved for validation")
    ap.add_argument("--test-ratio", type=float,
                    default=0.1,
                    help="fraction reserved for testing")
    ap.add_argument("--seed", type=int, default=1234,
                    help="seed used for random splitting")

    args = vars(ap.parse_args())

    indir      = args["indir"]
    outdir     = args["outdir"]
    listfile   = args["list"]
    prefix     = args["prefix"]
    val_ratio  = args["val_ratio"]
    test_ratio = args["test_ratio"]
    rng_seed   = args["seed"]
    with open(listfile) as lfile:
        images = [ l.strip() for l in lfile ]
    #
    # count records
    #
    num_images = len(images)
    #
    # random split
    #
    num_test  = int(num_images * test_ratio)
    num_val   = int(num_images * val_ratio)
    num_train = num_images - num_test - num_val

    random.seed(rng_seed)
    random.shuffle(images)

    #
    # generate HDF5 files
    #
    if num_train > 0:
        img_train = images[:num_train]
        train_out = os.path.join(outdir,prefix+'-train.h5')
        cfout = calamardo.CalamariFile(train_out,'w',max_samples=num_train)
        list_to_hdf5(cfout,indir,img_train)
        cfout.close()
    else:
        print('no training subset.')

    if num_val > 0:
        img_val   = images[num_train:(num_train+num_val)]
        val_out   = os.path.join(outdir,prefix+'-val.h5')
        cfout = calamardo.CalamariFile(val_out,'w',max_samples=num_val)
        list_to_hdf5(cfout,indir,img_val)
        cfout.close()
    else:
        print('no validation subset.')

    if num_test > 0:
        img_test  = images[-num_test:]
        test_out  = os.path.join(outdir,prefix+'-test.h5')
        cfout = calamardo.CalamariFile(test_out,'w',max_samples=num_test)
        list_to_hdf5(cfout,indir,img_test)
        cfout.close()
    else:
        print('no testing subset.')

