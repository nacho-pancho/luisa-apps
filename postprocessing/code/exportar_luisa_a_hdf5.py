#
# -*- coding:utf-8 -*-
#
#=======================================================

import imgdb                # base de datos de LUISA
import os                   # manejo de rutas
import skimage.io as imgio  # I/O de imagenes
import re                   # expresiones regulares
import numpy as np          # muy poca cosa
import h5py                 # I/O de archivos HDF5 (ubuntu: python3-h5py)

#=======================================================

IMGDIR='imgs'
OUTDIR='out'
DEBUGDIR='debug'
MARGIN=10
HDF5FILE='luisa.hdf5'

#=======================================================
#
# inicializamos estructura HDF5
#

cursor = imgdb.get_cursor()
cursor.execute("SELECT count(*) from bloque")
res = cursor.fetchone()
max_samples = res[0]

hdf5_file = h5py.File(HDF5FILE,'w')

block_coord_type = np.dtype('int16')
block_bits_type = h5py.vlen_dtype(np.dtype('uint8'))
block_text_type = h5py.vlen_dtype(h5py.string_dtype(encoding='utf-8'))

block_box_ds    = hdf5_file.create_dataset('top', (max_samples,4), dtype=block_coord_type)
block_bits_ds   = hdf5_file.create_dataset('bits', (max_samples,), dtype=block_bits_type,compression='lzf')
block_text_ds   = hdf5_file.create_dataset('text', (max_samples,), dtype=block_text_type)


#=======================================================
#
# Carga de datos desde DB a HDF5
# los bloques se agrandan con un margen de 10 pixeles a cada lado
#
rollos = [ r for r in imgdb.get_rollos()]
nb = 0
for rollo in rollos:
    num_rollo = rollo[0]
    dir_rollo = os.path.join(IMGDIR,f'r{num_rollo:04d}')
    dir_debug = os.path.join(DEBUGDIR,f'r{num_rollo:04d}')
    dir_out   = os.path.join(OUTDIR,f'r{num_rollo:04d}')
    if not os.path.exists(dir_debug):
        os.makedirs(dir_debug)
    if not os.path.exists(dir_out):
        os.makedirs(dir_out)
    hojas = [h for h in imgdb.get_hojas(num_rollo)]
    for hoja in hojas:
        hash_hoja  = hoja[6]
        rel_fname = hoja[2]
        rel_fname = re.sub(r'^r([0-9]{3})_(.*)$',r'r0\1_\2',rel_fname)
        fname_hoja = os.path.join(dir_rollo,rel_fname+'.png')
        print('\t',fname_hoja)
        img_hoja   = imgio.imread( fname_hoja).astype(np.uint8)
        nrows,ncols = img_hoja.shape
        img_debug = np.zeros((nrows,ncols,3))
        img_debug[:,:,0] = img_debug[:,:,1] = img_debug[:,:,2] = img_hoja
        bloques = [ b for b in imgdb.get_bloques(hash_hoja)]
        for bloque in bloques:
            hash_bloque = bloque[5]
            i0,j0,i1,j1 = bloque[1:5]
            i0 = max(i0-MARGIN,0)
            j0 = max(j0-MARGIN,0)
            i1 = min(i1+MARGIN,nrows)
            j1 = min(j1+MARGIN,ncols)
            bloque_out = img_hoja[i0:i1,j0:j1]
            rel_fname_bloque = f'{rel_fname}-{i0:04d}-{j0:04d}-{i1:04d}-{j1:04d}'
            fname_txt_bloque = os.path.join(dir_out,rel_fname_bloque + '.txt')
            print('\t\t',i0,j0,i1,j1, end=' ')
            textos = [ t[1].strip() for t in imgdb.get_texto(hash_bloque) if len(t[1].strip()) ]
            #
            # si no hay texto significativo, ignoramos bloque
            #
            nt = len(textos)
            if not nt:
                img_debug[i0:i1,j0:j1,1:] *= 0.5
                print('(empty)')
                continue
            #
            # para depuracion
            #
            img_debug[i0:i1,j0:j1,2] *= 0.5
            #
            # guarar en archivos
            #
            with open(fname_txt_bloque,'w') as ftxt:
                for t in textos:
                    print(t,file=ftxt)
            fname_img_bloque = os.path.join(dir_out,rel_fname_bloque+'.png')
            imgio.imsave(fname_img_bloque, bloque_out)
            #
            # guardar en HDF5
            #
            block_box_ds[nb]    = (i0,j0,i1,j1) 
            block_bits_ds[nb]   = np.packbits(bloque_out)
            block_text_ds[nb]   = textos            
            print(f'({nt} entries)')
            nb += 1
        fname_debug = os.path.join(dir_debug,rel_fname+'.png')
        imgio.imsave( fname_debug, img_debug)
