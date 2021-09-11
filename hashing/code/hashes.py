import hashlib
import subprocess
from PIL import Image
import numpy as np


def get_block_hash(imgname,i0,j0,i1,j1):
    return hashlib.sha256("{0:s}-{1:d}-{2:d}-{3:d}-{4:d}".format(imgname,i0,j0,i1,j1).encode(encoding='utf-8')).hexdigest()


def get_image_file_hash(fname):
    out = subprocess.run(('/usr/bin/sha256sum','-b',fname),capture_output=True)
    return out.stdout.split(b' ')[0].strip()


def get_image_pixels_hash(img):
    '''
    hash of image pixels.
    '''
    return None

def get_image_pixels_symhash(I):
    # ---------------------------------------------------
    # hacer algo en el medio
    # ---------------------------------------------------
    #
    # 8-way symmetric custom pixel-wise hash
    #
    # XOR of 4-neighbors
    # without center
    I1 = (I[:-2, 1:-1] + I[2:, 1:-1] + I[1:-1, :-2] + I[1:-1, 2:])
    I2 = (I[2:, 2:] + I[2:, :-2] + I[:-2, 2:] + I[:-2, :-2])
    # XOR of 4-neigbohrs
    P1 = np.sum(I1 % 2)
    # XOR of 4-diagonal neigbors
    P2 = np.sum(I2 % 2)
    # XOR of 8-neighbors
    P3 = np.sum((I1 + I2) % 2)
    HASH = P1 ^ P2 ^ P3


if __name__ == '__main__':
    hash = get_image_file_hash('/bin/sh')
    print(hash)
