#!/usr/bin/env python3
import os
import sys

import numpy as np
import calamardo
import skimage.io as imgio
import  random
import matplotlib.pyplot as plt

if __name__ == '__main__':
    if len(sys.argv) < 2:
        exit(1)
    cfin = calamardo.CalamariFile(sys.argv[1],'r')
    #
    # count records
    #
    n = cfin.len()
    empty = 0
    bad = 0
    ok = 0
    for i in range(n):
        img = cfin.get_image(i)
        txt = cfin.get_transcript(i).strip()
        print(np.max(img))
        #coin = random.random() > 0.99
        plt.figure()
        plt.imshow(img)
        plt.title(txt)
        plt.show()
        if len(txt) == 0:
            print('empty text!')
            empty += 1
        elif np.prod(img.shape) == 0:
            print('empty image!')
            empty += 1
        elif np.min(img) == np.max(img):
            print('blank image!')
            bad += 1
        else:
            ok += 1
        if i > 0 and not i % 100:
            print(f'{i:08d}/{n:08d}')
    print('samples',n,'ok',ok,'empty',empty,'bad',bad)
    cfin.close()

