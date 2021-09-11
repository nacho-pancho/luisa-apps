#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 12 17:22:41 FIRST_CROP18

@author: nacho
"""
#import os.path
import sys
import numpy as np
from PIL import Image,ImageOps,ImageChops,ImageDraw
from skimage import transform
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import os
import scipy.signal as dsp
import time
import argparse
import math
import functools # functional programming tools

#---------------------------------------------------------------------------------------

ROW_ABS_THRES = 20    # 
ROW_REL_THRES = 4     # 4 more pixels than local baseline
COL_ABS_THRES = 1     # column has at least three pixels black
COL_REL_THRES = 0.1   # the intensity of the column is less than 20% of the maximum
MIN_WORD_SEP = 20     # minimum separation between two words
MAX_LETTER_SEP = 18
BLOCK_ABS_THRES = 4   # minimum number of pixels in a valid block
TRAZO=1.0
COLOR=(0.0,0.2,0.4,0.1)
COLORMAP = plt.get_cmap('cool')
WIN_SIZE = 1024
MIN_ROW_HEIGHT = 20  # smallest letter I found was about 23
MAX_ROW_HEIGHT = 50  # smallest letter I found was about 50

#---------------------------------------------------------------------------------------

def imwrite(fname,img):
    '''
    simple wrapper for writing images, in case I change the I/O package
    '''
    img.save(fname,compression=COMP)

#---------------------------------------------------------------------------------------

def imrot(img,angle):
    w,h = img.size
    return img.rotate(angle, resample=Image.NEAREST,expand=True,fillcolor=1)

#---------------------------------------------------------------------------------------

def imread(fname):
    img = Image.open(fname)
    if fext.lower()[:3] != "tif":
        return img
    if not 274 in img.tag_v2:
        return img
    if img.tag_v2[274] == 8: # regression bug in PILLOW for TIFF images
        img = imrot(img,-90)
    return img

#---------------------------------------------------------------------------------------
    
def detect_bands(rmt, min_size):
    '''
    given a sequence of values, detects contiguous segments or 'bands' which are significantly
    darker than their neighborhood.
    '''
    # mark positions of up and down flanks
    dif = np.int8(rmt[1:]) - np.int8(rmt[:-1])
    upidx = np.flatnonzero(dif > 0) + 1
    dnidx = np.flatnonzero(dif < 0) + 1 

    # no up transitions
    if len(upidx) == 0:
        upidx = list()
        upidx.append(0)

    # no down transitions 
    if len(dnidx) == 0:
        dnidx = list()
        dnidx.append(len(rmt))
    
    # if first flank is down, assume there is an up flank at 0
    if (len(dnidx) > 1) & (dnidx[0] < upidx[0]): 
        upidx = np.insert(upidx,0,0)

    # more ups than downs means
    if len(upidx) > len(dnidx):
        dnidx = np.insert(dnidx,len(dnidx),len(rmt))
    
    bands = list(zip(upidx,dnidx))
    return bands



#---------------------------------------------------------------------------------------

def detect_rows(img,debugdir):
    #
    # remove margins from both sides, only for the purpose of
    # this analysis
    #
    row_sum = np.sum(img[:,300:-300],axis=1)

    # parameters of order filter
    radius  = 25
    domain  = np.arange(-radius,radius+1)
    order   = int((radius*2+1)/3)
    order   = 1
    row_sum_filtered    =  dsp.order_filter(row_sum,domain,order) 
    row_sum_thresholded = (row_sum > ROW_ABS_THRES) & ((row_sum - row_sum_filtered) > ROW_REL_THRES) #
    row_list = detect_bands(row_sum_thresholded, MIN_ROW_HEIGHT)
    band_heights = np.diff(row_list)
    if debugdir is not None:
        plt.close('all')
        fig = plt.figure(figsize=(16,10))
        plt.plot(row_sum*(100/I.shape[1]),lw=0.5)
        plt.plot(row_sum_filtered*(100/I.shape[1]),lw=0.5)
        plt.plot(1*row_sum_thresholded,lw=1)
        plt.legend(('sum','filt','thres'))
        for b in row_list:
            plt.plot(b,(100,100),lw=1,color='black')
        plt.grid(True)
        plt.savefig(os.path.join(debugdir,"row_sum.svg"),dpi=300)
        plt.close(fig)
    return row_list

#---------------------------------------------------------------------------------------

def label_row(img,row_info,row_stats):
    w,h = img.shape
    y0,y1 = row_info
    x0,x1 = 0,w
    w = x1 - x0
    h = y1 - y0
    
    if h < 10: # absolute height in pixels
        return 'flat'

    aspect = w / h
    row_img = img[y0:y1,x0:x1]
    #
    # trim row
    #
    ver_profile = np.sum(row_img,axis=1)
    nz          = np.flatnonzero(ver_profile)
    if len(nz) == 0:
        return 'empty'
    top, bottom = nz[0], nz[-1]

    hor_profile   = np.sum(row_img,axis=0)
    nz            = np.flatnonzero(hor_profile)
    left, right   = nz[0], nz[-1]
    trimmed_row   = row_img[top:bottom,left:right] 
    tw, th  = (right-left), (bottom-top)
    tsize   = tw * th
    if th == 0: # absolute height in pixels (smallest letter height ~ 20 pixels) 
        return 'flat'

    taspect = tw / th
    tsum = np.sum(trimmed_row)

    if th > 0.9*row_stats: # absolute height in pixels is more than twice the typical character height
        return 'tall'
    if th < 20: # absolute height in pixels (smallest letter height ~ 20 pixels) 
        return 'flat'
    if tsum > 0.7*tsize: # too dark
        return 'dark'
    if tsum < 0.025*tsize: # too empty
        return 'empty'
    else:
        return 'good'

#---------------------------------------------------------------------------------------

def refine_rows(img,row_list, debugdir):
    if len(row_list) == 0:
        return [],[]
    #
    # estadisticas
    #
    row_heights = [row_info[1]-row_info[0] for row_info in row_list if row_info[1] - row_info[0] > 20]
    if len(row_heights) == 0:
        print("AVISO: no hay filas suficientemente altas.",file=sys.stderr)
        return [],[]
    #
    # calculamos la moda de las alturas
    # sobre un histograma levemente suavizado
    #
    h,hc = np.unique(row_heights,return_counts=True)
    #
    # hack para convolucionar el histograma con un kernel exponencial
    #
    h0 = np.copy(hc)
    hc[1:]  = hc[1:] + 0.5*h0[:-1]
    hc[:-1] = hc[:-1] + 0.5*h0[1:]
    h0 = np.copy(hc)
    hc[1:] = hc[1:] + 0.5*h0[:-1]
    hc[:-1] = hc[:-1] + 0.5*h0[1:]
    row_height_mode = h[np.argmax(hc)]
    #print("mode=",row_height_mode)#
    # estimamos la forma típica de perfil de un renglón de texto
    # esto nos va a permitir detectar más fielmente las lineas de texto
    # usando un filtro apareado.
    #
    row_sum = np.sum(img[:,300:-300],axis=1)
    kernel_size = row_height_mode + 10
    kernel = np.zeros(kernel_size)
    if debugdir:
        fg = plt.figure(figsize=(10,10))
    naux = 0
    aux = np.zeros(kernel_size)
    for row_info in row_list:
        row_height = row_info[1] - row_info[0]
        aux[:] = 0
        dif = row_height - row_height_mode
        if np.abs(dif) <= 10:
            row_center = np.floor(row_info[0] + row_info[1])/2
            y0 = int(np.floor(row_center - kernel_size / 2 )) 
            if y0 < 0:
                continue
            if (y0+kernel_size) > len(row_sum):
                continue
            aux[:] = row_sum[y0:(y0+kernel_size)]         
            naux += 1 
            #print(row_info,row_height,"~")
        else:
            #print(row_info,row_height,"x")
            continue
        aux = aux * (1/ (np.linalg.norm(aux)+1e-5))
        kernel = kernel + aux
        if debugdir:
            plt.plot(aux,color=(0.5,0.5,0.5,0.5))
    #print("naux=",naux)
    if debugdir is not None:
        plt.plot(kernel/naux)
        plt.grid(True)
        plt.savefig(os.path.join(debugdir,"line_kernel.png"))
        plt.close(fg)

    kernel = kernel - np.mean(kernel)
    if np.linalg.norm(kernel) == 0:
        print("null kernel! cannot refine.",file=sys.stderr)
        return [],[]

    kernel = kernel / np.linalg.norm(kernel)
    
    refined_row_list = list()
    
    score = np.zeros(len(row_sum))
    for i in range(len(row_sum)-kernel_size):
        win = row_sum[ i : (i+kernel_size) ]
        win = win - np.mean(win)
        score[i] = np.dot( win, kernel )/( np.linalg.norm(win) + 1e-5 )

    i = 0
    match = np.zeros(len(score))
    MARGIN = 3
    while i < len(score):
        if score[i] > 0.6:
            match[i:(i+row_height_mode)] = 1
            refined_row_list.append((i,i+row_height_mode+2*MARGIN))
            i += row_height_mode-MARGIN 
        else:
            i += 1

    if debugdir is not None:
        fg = plt.figure(figsize=(20,20))
        plt.plot(row_sum[:-row_height_mode]/np.max(row_sum),lw=0.5)
        plt.plot(score,lw=0.5)
        plt.plot(match,lw=1.0)
        plt.grid(True)
        plt.savefig(os.path.join(debugdir,"row_profile.png"))
        plt.close(fg)

        fg = plt.figure()
        plt.bar(h,hc)
        plt.grid(True)
        plt.savefig(os.path.join(debugdir,"row_heights_hist.png"))
        plt.close(fg)
    
    row_list = refined_row_list
    row_labels = [label_row(img,bi,row_height_mode) for bi in row_list]
    #
    # 1. marcamos filas inútiles
    #
    if 0:
        lab,freq = np.unique(row_labels,return_counts=True)
        
        R = zip(row_list,row_labels)
        refined_row_list = [t[0] for t in R if t[1] != 'flat'] 

    
    return refined_row_list,row_labels # for now, only this

#---------------------------------------------------------------------------------------

def create_row_map(img,row_list,row_labels = None): 

    row_map = np.ones((img.shape[0],img.shape[1],3))
    row_map[:, :, 0 ] = (1-img).astype(float)
    row_map[:, :, 1 ] = row_map[:,:,0 ]
    row_map[:, :, 2 ] = row_map[:,:,0 ]
    w,h = img.shape
    for i in range(len(row_list)):
        info = row_list[i]
        y0,y1 = info[:2]
        x1 = w
        x0 = 0
        w,h = (x1-x0),(y1-y0)
        # for use with colormap 'RdYlGn' (red - yellow - green)
        cmap = cm.get_cmap('hsv')
        if row_labels is None:
            label = 'good'
        else:
            label = row_labels[i]
        if label == 'good':
            c = cmap(0.50)
        elif label == 'flat':
            c = cmap(0.10) 
        elif label == 'tall':
            c = cmap(0.30)
        elif label == 'empty':
            c = cmap(1.00)
        elif label == 'dark':
            c = cmap(0.80)
        else:
            print('Unkown label',label)
        row = row_map[y0:y1,x0:x1]
        bred   = row[:,:,0]
        bgreen = row[:,:,1]
        bblue  = row[:,:,2]
        bred[bred == 1] = c[0] 
        bgreen[bgreen == 1] = c[1] 
        bblue[bblue == 1] = c[2] 
        row_map[y0:y1,x0:x1,0] = bred
        row_map[y0:y1,x0:x1,1] = bgreen
        row_map[y0:y1,x0:x1,2] = bblue

    return row_map

#---------------------------------------------------------------------------------------

def merge_blocks(row_blocks):
    #
    # join accidentally separated letters
    # block : y0,x0,y1,x1
    nblocks = len(row_blocks)
    idx = 0
    while idx < (nblocks-1):   
        y0,x00,y1,x10 = row_blocks[idx]
        y0,x01,y1,x11 = row_blocks[idx+1]

        if (x01 - x10 ) < MAX_LETTER_SEP:
            merged_block = (y0,x00,y1,x11)
            del row_blocks[idx+1]
            del row_blocks[idx]
            row_blocks.insert(idx,merged_block)
            nblocks -= 1
        else:
            idx += 1
    return row_blocks

#---------------------------------------------------------------------------------------

def detect_blocks(img,row_list):
    #
    # cada rowa es luego cortada en bloques
    # para esto mide la intensidad promedio de cada columna en la rowa
    # y se recorta en donde dicha intensidad está por debajo de cierto umbral
    # (cero en este caso) y tiene un ancho suficientemente grande (más de 2 pixeles)
    #
    # aqui se detectan los bloques en cada rowa en base a las 
    # intensidades de las  columnas de pixeles
    #
    block_list = list()
    row_idx   = 0
    for row in row_list:
        y0 = row[0]
        y1 = row[1]
        Irow = I[y0:y1, :]
        col_sum = np.sum(Irow,axis=0)
        #
        col_sum_thresholded = (col_sum >= COL_ABS_THRES) 
        #
        # median filter to avoid
        #
        #col_sum_thresholded = dsp.medfilt(col_sum_thresholded, kernel_size=2*MIN_WORD_SEP+1)
        row_blocks          = detect_bands(col_sum_thresholded, MIN_WORD_SEP)
        row_block_list = [(y0,x0,y1,x1) for (x0,x1) in row_blocks] 
        row_block_list = merge_blocks(row_block_list)
        if len(row_block_list) > 0:
            block_list.append(row_block_list) # all row blocks in their own list
    #    
    # devolver resultado refinado
    #
    return block_list

#---------------------------------------------------------------------------------------


def label_block(img,block_info):
    y0,x0,y1,x1 = block_info
    w = x1 - x0
    h = y1 - y0
    aspect = w / h
    block_img = img[y0:y1,x0:x1]
    #
    # trim block
    #
    ver_profile = np.sum(block_img,axis=1)
    nz = np.flatnonzero(ver_profile)
    if len(nz) < 2:
        return 'flat'
    top, bottom = nz[0], nz[-1]

    hor_profile = np.sum(block_img,axis=0)
    nz = np.flatnonzero(hor_profile)
    if len(nz) < 2:
        return 'small'
    left, right = nz[0], nz[-1]
    trimmed_block = block_img[top:bottom,left:right] 
    tw, th  = (right-left), (bottom-top)
    tsize   = tw * th
    taspect = tw / th
    tsum = np.sum(trimmed_block) 

    if th < h/4: # relative height w.r.t. non trimmed block
        return 'flat'
    elif th < 20: # absolute height in pixels (smallest letter height ~ 20 pixels) 
        return 'flat'
    elif tsize < 400: # 20x20 pixels is really small 
        return 'small'
    elif taspect > 20: # too long for a single word
        return 'long'
    elif tw > 600: # too long for a single word
        return 'long'
    elif (tsum > 0.9*tsize) or (tsum > (tsize - BLOCK_ABS_THRES)): # too dark
        return 'dark'
    elif  tsum < BLOCK_ABS_THRES:
        return 'empty'
    else:
        return 'good'

#---------------------------------------------------------------------------------------

def break_long_block(img,block_info):
    '''
    Cuando un bloque es sospechosamente largo, hay básicamente dos posibilidades:
    - que sea texto subrayado, lo que no permite cortarlo 
    - que la separación entre palabras sea muy pequeña
    '''
    #
    # we take the average intensity from the upper half of the block and discard all the rows
    # below the first one that significantly surpasses that intensity 
    #
    y0,x0,y1,x1 = block_info
    block = img[y0:y1,x0:x1]
    h,w = block.shape
    col_sum = np.sum(block[:(h-5),:], axis=0) # small margin above underline
    col_sum_thresholded = col_sum > COL_ABS_THRES
    row_blocks          = detect_bands(col_sum_thresholded, MIN_WORD_SEP)
    row_block_list = [(y0,x0+xi,y1,x0+xf) for (xi,xf) in row_blocks] 
    if len(row_block_list) > 0:
        smaller_blocks = row_block_list # all row blocks in their own list
    else:
        smaller_blocks = list()
        smaller_blocks.append(block_info)
    return merge_blocks(smaller_blocks)

#---------------------------------------------------------------------------------------

def refine_blocks(img,block_list):
    '''
    El método primario  de recortar bloques es muy sencillo y rápido,
    pero no es capaz de discernir si cada bloque es en sí relevante.
    
    Además puede haber bloques mal segmentados.
    
    Finalmente, se realizan estadísticas para detectar, por ejemplo
    si la página debe ser girada -- si todos los bloques tienen más o menos
    el mismo tamaño, eso es un fuerte indicador de que el documento está girado 90
    grados.

    Esta función devuelve dos listas: una con las coordenadas ajustadas y otra con etiquetas indicando
    si los bloques deben borrarse, están mal segmentados, o sin dobles.
    
    Además devuelve un valor booleano indicando si la imagen debe ser girada

    '''
    #
    # 1. marcamos bloques inútiles: vacíos, basura, o sólo con puntuación 
    #
    refined_block_list = list()
    #
    # this list corresponds to the INPUT blocks, not the refined blocks
    # it is kept mostly for debugging to see why any given block was discarded
    #
    block_labels = list() 
    for row_block_list in block_list:
        refined_row_block_list = list()
        row_block_labels = list()
        for block_info in row_block_list:
            label = label_block(img,block_info)
            row_block_labels.append(label)
            if label == 'good':
                refined_row_block_list.append(block_info)
            elif label == 'long':
                # break long block into smaller ones
                # PENDING!  we ignore this for now!!
                smaller_blocks = break_long_block(img,block_info)
                if len(smaller_blocks) == 1:
                    refined_row_block_list.append(smaller_blocks[0])
                else:
                    refined_row_block_list.extend(smaller_blocks)
                # PENDING!
            else:
                # bad block, skip
                continue
        # only add row if non-empty
        block_labels.append(row_block_labels)
        if len(refined_row_block_list) > 0:
            refined_block_list.append(refined_row_block_list)
     
    return refined_block_list,block_labels 

#---------------------------------------------------------------------------------------

def create_block_map(img,block_list,block_labels = None):

    block_map = np.ones((img.shape[0],img.shape[1],3))
    block_map[:, :, 0 ] = (1-img).astype(float)
    block_map[:, :, 1 ] = block_map[:,:,0 ]
    block_map[:, :, 2 ] = block_map[:,:,0 ]

    for i in range(len(block_list)):
        row_block_list = block_list[i]
        row_block_labels = None
        if block_labels is not None:
            row_block_labels = block_labels[i]
        for j in range(len(row_block_list)):
            info = row_block_list[j]
            if row_block_labels is not None:
                label = row_block_labels[j]
            else:
                label = 'good'
            y0,x0,y1,x1 = info
            w,h = (x1-x0),(y1-y0)
            # for use with colormap 'RdYlGn' (red - yellow - green)
            cmap = cm.get_cmap('hsv')
            if label == 'good':
                c = cmap(0.50)
            elif label == 'long':
                c = cmap(0.20) 
            elif label == 'flat':
                c = cmap(0.10) 
            elif label == 'small':
                c = cmap(0.00)
            elif label == 'empty':
                c = cmap(0.40)
            elif label == 'dark':
                c = cmap(0.80)
            else:
                print('Unkown label',label)
            block = block_map[y0:y1,x0:x1]
            bred   = block[:,:,0]
            bgreen = block[:,:,1]
            bblue  = block[:,:,2]
            bred[bred == 1] = c[0] 
            bgreen[bgreen == 1] = c[1] 
            bblue[bblue == 1] = c[2] 
            block_map[y0:y1,x0:x1,0] = bred
            block_map[y0:y1,x0:x1,1] = bgreen
            block_map[y0:y1,x0:x1,2] = bblue

    return block_map

#---------------------------------------------------------------------------------------

if __name__ == '__main__':
    #
    # command line arguments
    #
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--prefix", type=str, default="../datos",
		    help="path prefix  where to find prealigned files")
    ap.add_argument("-o","--outdir", type=str, default="../results",
		    help="where to store results")
    ap.add_argument("-l","--list", type=str, default="../datos/r0566a.list",
		    help="text file where input pre-aligned files are specified")
    ap.add_argument("-X","--more-debug", action="store_true",
		    help="Save a LOT of debugging and diagnostic info (much slower!).")
    ap.add_argument("-D","--debug", action="store_true",
		    help="Save debugging and diagnostic info (much slower!).")
    ap.add_argument("-f","--force", action="store_true",
		    help="Forces the output to be overwritten even if it exists.")
    ap.add_argument("-m","--margin", type=int, default=0,
		    help="Cut this number of pixels from each side of image before analysis.")
    #
    # INICIALIZACION
    #
    args      = vars(ap.parse_args())
    print(args)
    prefix    = args["prefix"]
    outdir    = args["outdir"]
    list_file = args["list"]
    if args["debug"]:
        print(f"AVISO: modo depuracion, salida a {outdir}, lista {list}")
        #list_file = "../datos/debug.list" # lista especial con 5 imagenes por rollo
        #outdir="../debug"
    #
    # crear estructuras de directorios
    #
    with open(list_file) as fl:
        #
        # inicializacion de memoria
        #
        errors = list()
        nimage = 0
        t0 = time.time()
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
            relfname     = relfname.rstrip('\n')
            reldir,fname = os.path.split(relfname)
            fbase,fext   = os.path.splitext(fname)
            foutdir      = os.path.join(outdir,reldir)
            debugdir     = os.path.join(foutdir,fbase + "_debug")
            input_fname = os.path.join(prefix,relfname)
            fcsvblocks = os.path.join(foutdir,fbase + '.blocks')
            
            print(f'#{nimage} input={input_fname} outdir={outdir}')
            #
            # creamos carpeta de destino si no existe
            #
            fpath = fname[:(fname.find('/')+1)]

            if not args["force"] and os.path.exists(fcsvblocks):
                print('CACHED.')
                continue

            if not os.path.exists(foutdir):
                os.makedirs(foutdir)

            if args["more_debug"]:
                debugdir = os.path.join(foutdir,fbase + '_debug')
                if not os.path.exists(debugdir):
                    os.makedirs(debugdir)
            else:
                debugdir = None
            if not os.path.exists(input_fname):
                print("(input not found)")
                errors.append(input_fname)
                continue
            img = imread(input_fname)
            I = 1 - np.array(img)
            margin = args["margin"]
            if margin > 0:
                I = I[margin:-margin,margin:-margin]
            #
            # deteccion de bandas primaria
            #
            row_list = detect_rows(I,debugdir)
            #
            # refinamiento
            #
            refined_row_list, row_labels = refine_rows(I,row_list, debugdir)
            if args["more_debug"]:
                row_labels = ["good"] * len(row_list)
                row_map = create_row_map(I,row_list,row_labels)
                row_file = os.path.join(debugdir,fbase + "_raw_rows.jpg")
                plt.imsave(row_file,row_map)
                row_map = create_row_map(I,refined_row_list)
                row_file = os.path.join(debugdir,fbase + "_refined_rows.jpg")
                plt.imsave(row_file,row_map)
            
            block_list = detect_blocks(I,refined_row_list)
            #
            # refinamiento (se ve más de cerca cada bloque)
            #
            refined_block_list, block_labels = refine_blocks(I,block_list)
            #
            # imagen de analisis
            #
            if args["debug"]:
                block_map = create_block_map(I,block_list,block_labels)
                block_file = os.path.join(foutdir,fbase + "_raw_blocks.jpg")
                plt.imsave(block_file,block_map)
                block_map = create_block_map(I,refined_block_list)
                block_file = os.path.join(foutdir,fbase + "_refined_blocks.jpg")
                plt.imsave(block_file, block_map)
            #
            # importante para diagnostico
            # 
            #block_map = create_block_map(I,block_list,block_labels)
            #block_map = transform.resize(block_map, (block_map.shape[0] // 4, block_map.shape[1] // 4), anti_aliasing=True)
            #block_file = os.path.join(foutdir,fbase + ".blocks.png")
            #plt.imsave(block_file,block_map*(1/np.max(block_map)))
            #
            # guardamos lista de bloques en archivo CSV
            #
            fblocks = open(fcsvblocks,'w')
            row = 0
            for row_blocks in refined_block_list:
                col = 0
                for block in row_blocks:
                    blocktxt = functools.reduce(lambda a,b: str(a) + '\t' + str(b), block)
                    print(f"{row}\t{col}\t{blocktxt}", file=fblocks)
                    col += 1
                row += 1
            fblocks.close()
           #
            # fin loop principal
            #

        if nimage > 0:
            meandt = (time.time() - t0) / nimage
            print(f'Average time per image: {meandt} seconds. ')

        nerr = len(errors)
        if nerr > 0:
            print(f'ERROR AL PROCESAR {nerr} ARCHIVOS:')
            for l in errors:
                print(l)
        else:
            print("completo.")
        #
        # fin main
        #
#---------------------------------------------------------------------------------------
