#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
Falta
'''
import matplotlib.pyplot as plt # ploteo
import numpy as np             # matrices
import numpy.random as rng     # random numbers
import scipy.ndimage.filters as dsp # digital signal processing
import argparse                # para procesar linea de comandos
from PIL import Image
from matplotlib import cm
from matplotlib.widgets import Slider, Button, RadioButtons

#
# global variables
#
image_fig = None
stint = None
snoise1 = None
snoise2 = None
sscale1 = None
sblur1 = None
sscale2 = None
sthres = None
step1_ax = None
step2_ax = None
step3_ax = None
step4_ax = None

clean_array = None


def show_text(ax,text_array):
    ax.imshow(1-text_array,cmap=plt.get_cmap('gray'),vmin=0,vmax=1)
    ax.set_axis_off()

def update(val):
    global degraded_array
    global stint,snoise1,snoise2,sblur1,sscale1,sscale2,sthres

    tint = stint.val
    noise_power_1 = snoise1.val
    noise_power_2 = snoise2.val
    blur_radius_1 = sblur1.val
    noise_scale_1 = sscale1.val
    noise_scale_2 = sscale2.val
    threshold     = sthres.val

    #
    # primera etapa: ruido Poisson correlacionado
    # simula asperezas en la hoja, que varian la
    # intensidad de la tinta dentro de una letra
    # esto se deberia manifestar como pozos con menos
    # tinta dentro de las letras, pero no afectar al fondo 
    #
    print(f"tint intensity {tint}")
    print(f"noise power 1 {noise_power_1}")
    print(f"noise power 2 {noise_power_2}")
    print(f"blur radius 1 {blur_radius_1}")
    print(f"noise scale 2 {noise_scale_1}")
    print(f"noise scale 3 {noise_scale_2}")
    print(f"--tint={tint} --noise1={noise_power_1} --noise2={noise_power_2} --blur={blur_radius_1} --scalex={noise_scale_2} --scaley={noise_scale_2} --thres={threshold}")
    tmph = int(clean_array.shape[0]/noise_scale_1)
    tmpw = int(clean_array.shape[1]/noise_scale_1)
    
    noise1 = rng.uniform(0,noise_power_1,size=(tmph,tmpw))
    noise1 = np.asarray(Image.fromarray(noise1).resize(size=(clean_array.shape[1],clean_array.shape[0]),resample=Image.LANCZOS))
    #
    # scale the noise
    #
    degraded_array = tint*clean_array
    degraded_array = np.minimum(1,np.maximum(0,tint*(clean_array - noise1)))
    show_text(step1_ax,degraded_array)

    #
    # luego se agrega ung borroneado para simular la difusion de la tinta
    #
    degraded_array = dsp.gaussian_filter(degraded_array,sigma=blur_radius_1)
    show_text(step2_ax,degraded_array)
    #image_axes.imshow(degraded_array,cmap=plt.get_cmap('gray'))
    #
    # finalmente se agrega un ruido al papel de fondo para simular
    # la textura de la hoja
    #
    tmpw = int(clean_array.shape[1]/noise_scale_2)
    tmph = int(clean_array.shape[0]/noise_scale_2)
    noise2 = rng.uniform(0,noise_power_2,size=(tmph,tmpw))
    noise2 = np.asarray(Image.fromarray(noise2).resize(size=(clean_array.shape[1],clean_array.shape[0]),resample=Image.LANCZOS))

    noise2 = noise2 * (1-degraded_array)
    degraded_array = degraded_array + noise2
    degraded_array = np.maximum(0,degraded_array) 
    show_text(step3_ax,degraded_array)
    
    degraded_array = degraded_array > threshold
    show_text(step4_ax,degraded_array)

    image_fig.canvas.draw_idle()

def reset(event):
    stint.reset()
    snoise1.reset()
    snoise1.reset()
    sblur1.reset()
    sscale1.reset()
    sscale2.reset()
    sthres.reset()
    update(event)

#==============================================================================
# MAIN

if __name__ == '__main__':

    #
    # procesamiento de linea de comandos usando argparse
    #
    
    clean_image = Image.open('../data/sample.tif').convert('L')
    clean_array = 1.0-np.array(clean_image).astype(np.float)*(1.0/255.0)
 
    image_fig,splots = plt.subplots()
    splots.set_axis_off()
    aspect = clean_array.shape[1]/clean_array.shape[0]
    axcolor = 'lightgoldenrodyellow'
    step0_ax = plt.axes([0.1, 0.84, 0.1*aspect, 0.1], facecolor=axcolor, xmargin=0, ymargin=0, aspect=aspect, frame_on=False)
    step0_ax.imshow(1-clean_array,cmap=plt.get_cmap('gray'))
    step1_ax = plt.axes([0.1, 0.73, 0.1*aspect, 0.1], facecolor=axcolor, xmargin=0, ymargin=0, aspect=aspect, frame_on=False)
    step1_ax.imshow(clean_array,cmap=plt.get_cmap('gray'))
    step1_ax.set_axis_off()
    step2_ax = plt.axes([0.1, 0.62, 0.1*aspect, 0.1], facecolor=axcolor)
    step2_ax.imshow(clean_array,cmap=plt.get_cmap('gray'))
    step2_ax.set_axis_off()
    step3_ax = plt.axes([0.1, 0.51, 0.1*aspect, 0.1], facecolor=axcolor)
    step3_ax.imshow(clean_array,cmap=plt.get_cmap('gray'))
    step3_ax.set_axis_off()
    step4_ax = plt.axes([0.1, 0.4, 0.1*aspect, 0.1], facecolor=axcolor)
    step4_ax.imshow(clean_array,cmap=plt.get_cmap('gray'))
    step4_ax.set_axis_off()
    plt.subplots_adjust(left=0.0, bottom=0.5)
 
    axnoise1 = plt.axes([0.1, 0.25, 0.3, 0.03], facecolor=axcolor)
    axnoise2 = plt.axes([0.1, 0.20, 0.3, 0.03], facecolor=axcolor)
    axscale1 = plt.axes([0.1, 0.15, 0.3, 0.03], facecolor=axcolor)
    axscale2 = plt.axes([0.1, 0.10, 0.3, 0.03], facecolor=axcolor)
    axtint   = plt.axes([0.6, 0.25, 0.3, 0.03], facecolor=axcolor)
    axblur1  = plt.axes([0.6, 0.20, 0.3, 0.03], facecolor=axcolor)
    axthres  = plt.axes([0.6, 0.15, 0.3, 0.03], facecolor=axcolor)
    resetax  = plt.axes([0.6, 0.10, 0.3, 0.04])

    stint  = Slider(axtint, 'tint   ', 0.0, 1.0, valinit=0.5)
    snoise1  = Slider(axnoise1, 'noise 1', 0.0, 1.0, valinit=0.5)
    snoise2  = Slider(axnoise2, 'noise 2', 0.0, 1.0, valinit=0.5)
    sblur1  = Slider(axblur1, 'blur 1', 0.0, 3.0, valinit=0.8)
    sscale1  = Slider(axscale1, 'scale 1', 0.0, 5.0, valinit=3)
    sscale2  = Slider(axscale2, 'scale 2', 0.0, 5.0, valinit=2)
    
    sthres  = Slider(axthres, 'threshold', 0.0, 1.0, valinit=0.6)

    button = Button(resetax, 'Reset', color=axcolor, hovercolor='0.975')

    stint.on_changed(update)

    snoise1.on_changed(update)
    snoise2.on_changed(update)

    sblur1.on_changed(update)
    sscale1.on_changed(update)
    sscale2.on_changed(update)

    sthres.on_changed(update)
    
    button.on_clicked(reset)
    plt.show()

