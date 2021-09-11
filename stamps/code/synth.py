#!/usr/bin/env python3
#
# -*- coding: utf-8 -*-
"""

@author: nacho
"""
#
# # paquetes base de Python3 (ya vienen con Python)
#
import os.path
import argparse
#
# bibliotecas adicionales necesarias
#
import numpy as np
from PIL import Image
import scipy.signal as dsp
import skimage.io as imgio
from skimage import transform,io # pip3 install scikit-image

verbose = False

#---------------------------------------------------------------------------------------


if __name__ == '__main__':
    #
    # ARGUMENTOS DE LINEA DE COMANDOS
    #
    ap = argparse.ArgumentParser()
    ap.add_argument("-S", "--stampdir", type=str, default="/datos/luisa/sellos_clasificados_original/",
      help="path prefix  where to find files")
    ap.add_argument("-o", "--outdir", type=str, default="/luisa/sellos/sintetizados/",
      help="where synthesized stamps are stored")
    ap.add_argument("-l","--list", type=str, default="",
      help="text file where input files are specified")
    args = vars(ap.parse_args())
    #
    # INICIALIZACION
    #
    list_file  = args["list"]
    if len(list_file) == 0:
        print("ERROR: must specify list file")
        exit(1)

    stampdir = args["stampdir"]
    outdir  = args["outdir"]
    if not os.path.exists(outdir):
        os.makedirs(outdir,exist_ok=True)

    shift_max = 30
    shift_step = 1

    angle_max = 8
    angle_step = 0.2

    angles = np.arange(-angle_max, angle_max+angle_step, angle_step)
    shifts = np.arange(-shift_max,shift_max+shift_step,step=shift_step)

    scale_max = 1.3
    scale_exp = np.log(scale_max)
    scale_step = scale_exp/10
    scales = np.exp(np.arange(-scale_exp,scale_exp+scale_step,scale_step))
    num_angles = len(angles)
    num_shifts = len(shifts)
    num_scales = len(scales)

    #
    # first pass: scan stamps, sizes, define canvas
    #
    nstamps = 0
    nclasses = 0
    maxw = 0
    maxh = 0
    print('FIRST PASS')
    originals = list()
    with open(list_file) as fl:
        for relfname in fl:
            #
            # locations, filenames, etc.
            #
            relfname = relfname.rstrip('\n')
            reldir,fname = os.path.split(relfname)
            fbase,fext = os.path.splitext(fname)
            input_fname = os.path.join(stampdir,relfname)
            stamp = (imgio.imread(input_fname)/255).astype(float)
            stamp = transform.rescale(stamp,0.5,anti_aliasing=1,order=3)
            h,w = stamp.shape
            if w > maxw:
                maxw = w
            if h > maxh:
                maxh = h
            originals.append((reldir,fname,stamp.astype(np.float)))

    canvas_width = int(np.ceil(scale_max*maxw+2*shift_max))
    canvas_height = int(np.ceil(scale_max*maxh+2*shift_max))
    offset_h = (canvas_height - maxh ) //2
    offset_w = (canvas_width - maxw ) //2

    padded = list()
    nstamps = len(originals)

    print('NUMBER OF STAMPS:',nstamps)
    print('MAX WIDTH',maxw,'MAX HEIGHT',maxh)
    print('CANVAS WIDTH',canvas_width,'MAX HEIGHT',canvas_height)

    for i in range(len(originals)):
        padded_stamp = np.zeros((canvas_height,canvas_width))
        reldir,fname,stamp = originals[i]
        h,w = stamp.shape
        padded_stamp[offset_h:(offset_h+h),offset_w:(offset_w+w)] = 1-stamp
        padded.append(padded_stamp)
        outfile = os.path.join(outdir,fname)
        imgio.imsave(outfile,(255*padded_stamp).astype(np.uint8))

    num_pivots = nstamps
    print('number of shifts:',num_shifts)
    print('number of angles:',num_angles)
    print('number of scales:',num_scales)
    print('number of pivots:',num_pivots)
    print('total combinations to be tested:',num_shifts*num_angles*num_scales*num_pivots)

    best_pivot_score = -100000
    for i,pivot in enumerate(padded):

        pivot_score = 0
        fused = pivot.astype(np.float)
        imgio.imsave(os.path.join(outdir, f'pivot_{i:03d}.png'), (255*pivot).astype(np.uint8))
        pivot_norm = np.linalg.norm(pivot.ravel())
        for j,stamp in enumerate(padded):

            if np.all(stamp == pivot):
                continue

            best_score = 0
            best_transf = ()
            for scale in scales:
                aux_scaled_stamp = transform.rescale(stamp,scale,anti_aliasing=True,order=3)
                sh,sw = aux_scaled_stamp.shape
                scaled_stamp = np.zeros((canvas_height,canvas_width))
                if scale < 1:
                    offseth = (canvas_height-sh)//2
                    offsetw = (canvas_width-sw)//2
                    scaled_stamp[offseth:(offseth+sh),offsetw:(offsetw+sw)] = aux_scaled_stamp
                else:
                    offseth = (sh-canvas_height)//2
                    offsetw = (sw-canvas_width)//2
                    scaled_stamp[:,:] = aux_scaled_stamp[offseth:(offseth+canvas_height),offsetw:(offsetw+canvas_width)]

                for angle in angles:
                    rotated_scaled_stamp = transform.rotate(scaled_stamp,angle,order=3)

                    for shift in shifts:
                        rotated_scaled_shifted_stamp = np.zeros((canvas_height,canvas_width))
                        if shift > 0:
                            rotated_scaled_shifted_stamp[shift:,shift:] = rotated_scaled_stamp[:-shift,:-shift]
                        elif shift < 0:
                            rotated_scaled_shifted_stamp[:shift,:shift] = rotated_scaled_stamp[-shift:,-shift:]
                        else:
                            rotated_scaled_shifted_stamp = rotated_scaled_stamp

                        stamp_norm = np.linalg.norm(rotated_scaled_shifted_stamp.ravel())
                        score = np.sum(rotated_scaled_shifted_stamp * pivot) / (pivot_norm * stamp_norm)
                        #print(f'pivot {i} stamp {j} scale {scale:6.3f} angle {angle:6.3f} shift {shift} score {score:6.3f}')
                        if score > best_score:
                            best_score = score
                            best_transf = (scale,angle,shift,rotated_scaled_shifted_stamp)

            print(f'pivot {i} stamp {j} best score {best_score}')

            imgio.imsave(os.path.join(outdir,f'pivot_{i:03d}_stamp_{j:03d}_orig.png'),(255*stamp).astype(np.uint8))
            imgio.imsave(os.path.join(outdir,f'pivot_{i:03d}_stamp_{j:03d}.png'),(255*best_transf[3]).astype(np.uint8))
            imgio.imsave(os.path.join(outdir,f'pivot_{i:03d}_stamp_{j:03d}_dif.png'),(255*np.abs(best_transf[3]-pivot)).astype(np.uint8))
            pivot_score -= np.abs(scale-1)*10+np.abs(shift)+np.abs(angle)
            fused += rotated_scaled_shifted_stamp
        print(f'pivot {i}  pivot score {pivot_score}')
        fused /= nstamps
        if pivot_score > best_pivot_score:
            best_pivot_score = pivot_score
            best_pivot = (i,pivot,fused)
        print(np.max(fused))
        imgio.imsave(os.path.join(outdir,f'pivot_{i:03d}_fused.png'),(255*fused).astype(np.uint8))

    imgio.imsave(os.path.join(outdir,'best_pivot.png'),(255*best_pivot[2]).astype(np.uint8))
    print(f'best pivot {best_pivot[0]}')

    #
    # fin main
    #
#---------------------------------------------------------------------------------------
