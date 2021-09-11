#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrae las lineas de texto como imágenes de un archivo HDF5 generado por el paquete
calamardo y ejecuta el Tesseract sobre ellas, generando una transcripción que
a su vez es almacenada en el HDF5
@author: nacho
"""
#
# paquetes base de Python3 (ya vienen con Python)
#
import time
import argparse
import subprocess
import os

# paquetes adicionales
#
import numpy as np
import skimage.io as imgio
#
# propios
#
import calamardo
import corrector

#---------------------------------------------------------------------------------------

def execute_tesseract(image,tmpdir='/tmp'):
    image = 255*(1-image) # binary to 8 bit grayscale
    imgio.imsave(os.path.join(tmpdir,'line.tif'),(255*image).astype(np.uint8))
    #command = 'tesseract --dpi 400 --psm 7 -l spa /tmp/line.tif /tmp/line'
    command = f'tesseract --dpi 400 --psm 13 -l spa  {tmpdir}/line.tif {tmpdir}/line'
    subprocess.run(command, shell=True,capture_output=True)
    with open(os.path.join(tmpdir,'line.txt'),'r') as f:
        line = f.readline().strip()
        return line

#---------------------------------------------------------------------------------------

if __name__ == '__main__':
    #
    # ARGUMENTOS DE LINEA DE COMANDOS
    #
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", type=str, default="",
		    help="HDF5 file to process")
    ap.add_argument("--outdir", type=str, default='',
		    help="if specified, save training data in specified directory")
    ap.add_argument("--dict", type=str,
                    default="/datos/luisa/diccionarios/todo.txt",
                    help="Dictionary of valid words")
    ap.add_argument("--corpus", type=str,
                    default="../data/benito_perez_galdos_all.txt",
                    help="Text corpus to train language model")
    ap.add_argument("--tmpdir", type=str, default='/tmp',
		    help="directory to store temporary files")
    ap.add_argument("--force", type=bool, default=False,
		    help="overwrite previously generated transcriptions")
    #
    # INICIALIZACION
    #
    
    args = vars(ap.parse_args())
    hdf5_file = args["file"]
    outdir = args["outdir"]
    #
    if not len(hdf5_file):
        exit(1)

    file    = calamardo.CalamariFile(hdf5_file,'r+')
    n = file.len()
    
    save_dir  = len(outdir) > 0
    if save_dir:
        os.makedirs(outdir,exist_ok=True)

    corr = corrector.Corrector(args["dict"])
    accepted = 0
    total    = 0
    i = 0
    emptyimgcounter = 0
    for i in range(n):
        t0 = time.time()
        image = file.get_image(i)
        if not np.prod(image.shape) or np.max(image) == np.min(image):
            print('empty image')
            emptyimg = True
            emptyimgcounter += 1
            if emptyimgcounter >= 100:
                print('no more images.')
                break
            else:
                continue
        else:
            emptyimgcounter = 1
        
        raw_text = execute_tesseract(image,tmpdir=args['tmpdir'])
        print(f'{i:6d}:{raw_text:60s} --> ',end='')
        corrected_text, total_error, error_code = corr.correct_line(raw_text,ignore_tails=True)
        max_error = max(1,len(raw_text) // 10) 
        print(f'{corrected_text:60s} | largo {len(raw_text):3d} maxerr {max_error:3d} err {total_error:3d}',end=' ')
        if total_error > max_error:
            print('-DISCARD- (garbage)')
            file.set_transcript(i,"<<DISCARDED>>")
        elif error_code == corrector.TOO_FEW_WORDS:
            print('-DISCARD- (too few words)')
            file.set_transcript(i,"<<DISCARDED>>")
        elif error_code == corrector.TOO_MANY_SHORT:
            print('-DISCARD- (too many short words)')
            file.set_transcript(i,"<<DISCARDED>>")
        else:
            print('-ACCEPT-')
            accepted += 1
            if save_dir:
                imgio.imsave(os.path.join(outdir,f'{i:08d}.tif'),(255*image).astype(np.uint8))
                ftxt = open(os.path.join(outdir,f'{i:08d}.gt.txt'),'w')
                print(corrected_text,file=ftxt)
                ftxt.close()
                
            file.set_transcript(i,corrected_text)
        total += 1

    paccepted = int(100.0 * accepted / total)
    pdiscarded = 100 - paccepted
    print('total lines ',total, ' accepted ',accepted, '(',paccepted,') discarded',total-accepted,'(',pdiscarded,')' )
    file.close()
    #
    # fin main
    #
    
#---------------------------------------------------------------------------------------
