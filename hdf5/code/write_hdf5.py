#!/usr/bin/python3
# -*- coding: utf-8 -*-
import h5py
import numpy as np
from PIL import Image,ImageChops,ImageDraw
import matplotlib.pyplot as plt
import os

print("Creamos el archivo")

max_samples = 512

comp= 'lzf'

hdf5_file = h5py.File('foo.hdf5','w')

block_hash_type = np.dtype('byte')
block_bits_type = h5py.vlen_dtype(np.dtype('uint8'))
block_dim_type = np.dtype('int16')
block_text_type = h5py.string_dtype(encoding='utf-8')


block_hash_ds = hdf5_file.create_dataset('hash', (max_samples,64), dtype=block_hash_type,compression=comp)
block_dim_ds  = hdf5_file.create_dataset('dim', (max_samples,2), dtype=block_dim_type,compression=comp)
block_bits_ds = hdf5_file.create_dataset('bits', (max_samples,), dtype=block_bits_type,compression=comp)
block_text_ds = hdf5_file.create_dataset('text', (max_samples,), dtype=block_text_type,compression=comp)

with open('blocks.list') as list_file:
    block_idx = 0
    for block_fname in list_file:
        block_fname = block_fname.strip()
        block_path,block_tail = os.path.split(block_fname)
        block_image = Image.open(block_fname,'r')
        block_hash = bytes(block_tail[:64],'ascii')
        print(block_hash)
        text_tail = block_tail[:64] + '.txt'
        #print('block_tail:', block_tail)
        #print('text_tail:',  text_tail)
        text_fname = os.path.join(block_path,text_tail)
        #print('text_fname:',  text_fname)
        block_size = block_image.size # imaging convention: width,height
        block_dim = (block_size[1],block_size[0]) # matrix convention: height,width
        block_pixels = np.array(block_image.getdata())
        block_len = np.prod(block_dim)
        #print('array:', block_dim,block_len,end=' ')
        #print('bytes:', block_pixels.shape,end=' ')
        block_bits = np.packbits(block_pixels)
        text_file = open(text_fname)
        block_text = text_file.readline().strip()
        text_file.close()

        block_hash_ds[block_idx] = np.frombuffer(block_hash,dtype=np.uint8)
        block_dim_ds[block_idx] = block_dim
        block_bits_ds[block_idx] = block_bits
        block_text_ds[block_idx] = block_text

        print('text:',block_text)
        print('dim:',block_dim)
        print('pixels:',block_pixels.shape)
        block_idx = block_idx + 1
        #plt.imshow(block_image)
        #plt.title(block_text)
        #plt.show()
        if np.mod(block_idx,1000) == 0:
            print('Calma... solo faltan ',str(662994-block_idx))
hdf5_file.close()
