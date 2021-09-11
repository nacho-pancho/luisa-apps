#!/usr/bin/python3
# -*- conding: utf-8 -*-
'''
This file shows how to open and read the hackathon data
stored in the HDF5 data file format.

The HDF5 format is handled by the h5py Python package,
accesible through pip (pip3)

Each HDF5 file in the Hackathon corpus contains three datasets.
Each dataset is accessed using a keyword. In our case the
keywords are:

- 'text' ... text corresponding to a block
- 'bits' ... pixel data of a block
             pixels are binary; their bit values are packed into bytes
             in the dataset
- 'dim' .... dimensions (height,width) of a block
             notice that blocks vary in shape, so this info is important

Each dataset is an indexed list of entries. The same index
corresponds to the same block in all three datasets, so that
text[0] is the text corresponding to the image contained in bits[0]
which has to be reshaped to dim[0] before processing.
'''
#
# DEPENDENCIES
#
import h5py                      # HDF5 I/O library
import numpy as np
import matplotlib.pyplot as plt  # show stuff
#
# BEGIN
#
hdf5_fname = 'foo.hdf5'
with h5py.File(hdf5_fname, 'r') as hdf5_file:  # Pythonic way to open a file
    #
    # get the three datasets
    #
    block_hash_ds = hdf5_file['hash']
    block_text_ds = hdf5_file['text']
    block_dim_ds = hdf5_file['dim']
    block_bits_ds = hdf5_file['bits']
    print(len(block_text_ds))
    #
    # read the entries in the dataset sequentially
    # starting at index 0
    block_idx = 0                                        # first index to read
    while len(block_text_ds[block_idx]) > 0:
        #
        # read block info
        #
        block_hash = block_hash_ds[block_idx].tobytes()  # get hash for current block
        block_text = block_text_ds[block_idx]            # get text for current block
        block_dim =  block_dim_ds[block_idx]             # get dimension for current block
        block_len = int(block_dim[0])*int(block_dim[1])  # number of pixels
        block_bits = block_bits_ds[block_idx]            # get packed bits
        block_pixels = np.unpackbits(block_bits)         # unpack bits into boolean pixels
        block_pixels = block_pixels[:block_len]          # discard trailing bits generate during packing
        block_array = np.reshape(block_pixels, block_dim) # reshape pixels as 2D image
        #
        # show block info
        #
        print('idx:', block_idx, end=' ')
        print('hash:', block_hash, end=' ')
        print('text:', block_text, end=' ')
        print('dim:', block_dim)
        plt.imshow(block_array) # show the image
        plt.title(block_text + ' ' + str(block_dim))
        plt.show()
        #
        # go to next block
        #
        block_idx = block_idx + 1
#
# END
#