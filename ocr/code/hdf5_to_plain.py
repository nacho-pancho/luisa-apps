#!/usr/bin/env python3
import os
import sys

import numpy as np
import calamardo
import skimage.io as imgio

if __name__ == '__main__':
    if len(sys.argv) < 3:
        exit(1)
    cfin = calamardo.CalamariFile(sys.argv[1],'r')
    dout = sys.argv[2]
    iin = 0
    iout = 0
    emptycount = 0
    nempty = 0
    ndiscard = 0
    #
    # count records
    #
    n = cfin.len()
    for i in range(n):
        img = cfin.get_image(i)
        txt = cfin.get_transcript(i)
        imgfname = os.path.join(dout,f'{i:08d}.tif')
        txtfname = os.path.join(dout,f'{i:08d}.gt.txt')
        print(imgfname,txtfname)
        if np.max(img) == 1:
            img = (255-255*img).astype(np.uint8)
        imgio.imsave(imgfname,img)
        with open(txtfname,'w') as f:
            print(txt,file=f)
        if i > 0 and not i % 100:
            print(f'{i:08d}/{n:08d}')
    cfin.close()

