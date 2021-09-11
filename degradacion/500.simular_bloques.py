#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
Dado un rollo de microfilmado, selecciona bloques bien transcriptos por el OCR en las hojas
que tienen un score global por encima de cierto umbral.
A esos bloques se les genera versiones distorsionadas según parámetros especificados por el usuario
(ruido y umbral)

presets:

demasiado claro 1
--tint=0.5 --noise1=0.5 --noise2=0.5 --blur=0.8 --xscale=2 --yscale=2 --thres=0.6 

demasiado claro 2

--tint=0.5 --noise1=0.5 --noise2=0.34 --blur=0.8 --xscale=3.3 --yscale=3.3 --thres=0.48

demasiado claro 3

--tint=0.5 --noise1=0.5 --noise2=0.34 --blur=0.8 --xscale=3.3 --yscale=3.3 --thres=0.41

demasiado oscuro / intermedio
--tint=0.5 --noise1=0.5 --noise2=0.20 --blur=0.8 --xscale=2 --yscale=2 --thres=0.22

demasiado oscuro / ruido gordo
--tint=0.5 --noise1=0.97 --noise2=0.05 --blur=1.65 --xscale=4.8 --yscale=4.8 --thres=0.05

demasiado oscuro / ruido fino

--tint=0.5 --noise1=0.97 --noise2=0.05 --blur=1.64 --xscale=0.91 --yscale=0.91 --thres=0.05

select bloques.text from hojas,bloques where hojas.score > 0.7 and bloques.hoja=hojas.nombre and bloques.score=1;

Entradas:
  rollo 
  umbral (entre 0 y 1)
'''
import os                      # manejo de archivos
import matplotlib.pyplot as plt # ploteo
import numpy as np             # matrices
import scipy.ndimage.filters as dsp # digital signal processing
import argparse                # para procesar linea de comandos
import imgdb
from PIL import Image,ImageFilter,ImageChops
import config
import numpy.random as rng

#==============================================================================
# MAIN


def bool_array_to_pil_img(data):
    size = data.shape[::-1]
    databytes = np.packbits(data, axis=1)
    return Image.frombytes(mode='1', size=size, data=databytes)

def degrade_text(clean_array,args):

    tint          = float(args['tint'])
    noise_power_1 = float(args['noise1'])
    noise_power_2 = float(args['noise2'])
    blur_radius_1 = float(args['blur'])
    noise_scale_1 = float(args['xscale'])
    noise_scale_2 = float(args['yscale'])
    threshold     = float(args['thres'])

    #
    # primera etapa: ruido Poisson correlacionado
    # simula asperezas en la hoja, que varian la
    # intensidad de la tinta dentro de una letra
    # esto se deberia manifestar como pozos con menos
    # tinta dentro de las letras, pero no afectar al fondo 
    #

    tmph = int(clean_array.shape[0]/noise_scale_1)
    tmpw = int(clean_array.shape[1]/noise_scale_1)
    
    noise1 = rng.uniform(0,noise_power_1,size=(tmph,tmpw))
    noise1 = np.asarray(Image.fromarray(noise1).resize(size=(clean_array.shape[1],clean_array.shape[0]),resample=Image.LANCZOS))
    #
    # scale the noise
    #
    degraded_array = tint*clean_array
    degraded_array = np.minimum(1,np.maximum(0,tint*(clean_array - noise1)))

    #
    # luego se agrega ung borroneado para simular la difusion de la tinta
    #
    degraded_array = dsp.gaussian_filter(degraded_array,sigma=blur_radius_1)
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
    
    degraded_array = degraded_array > threshold
    return 1.0-degraded_array    


if __name__ == '__main__':
    #
    # procesamiento de linea de comandos usando argparse
    #
    ap = argparse.ArgumentParser()
    ap.add_argument("-r", "--rollo", 
        help="rollo a procesar")
    ap.add_argument("-d", "--outdir", required=True, 
        help="directorio de salida")
    ap.add_argument("-H", "--hoja", 
        help="hoja a procesar (por defecto todas en el rollo)")
    ap.add_argument("-t", "--tint", default=0.5,
        help="intensidad de la tinta impresa")
    ap.add_argument("-u", "--thres", default=0.3,
        help="umbral sobre el cual se considera 'negro' un pixel")
    ap.add_argument("-n", "--noise1", default=0.8,
        help="intensidad del ruido aplicado ANTES del borroneo (blur)")
    ap.add_argument("-N", "--noise2", default=0.1,
        help="intensidad del ruido aplicado LUEGO del borroneo (blur)")
    ap.add_argument("-x", "--xscale", default=1.5,
        help="escala horizontal del ruido aplicado ANTES del borroneo; vendría a ser el grano del papel")
    ap.add_argument("-y", "--yscale", default=1.0,
        help="escala vertical del ruido aplicado ANTES del borroneo; vendría a ser el grano del papel")
    ap.add_argument("-b", "--blur", default=1.5,
        help="borroneo de la imagen escaneada")
    ap.add_argument("-q", "--min-quality", default=0.8,
        help="Calidad (score) minimo para considerar los bloques de una imagen en la simulacion")
    ap.add_argument("-g", "--ground-truth", default=False,
        help="save ground truth as well")

    args = vars(ap.parse_args())
    umbral = args['thres']
    rollo = args['rollo']
    hoja = args['hoja']
    outdir = args['outdir']
    basedir = config.ALIGNED_DIR

    if not os.path.exists(outdir):
        os.mkdir(outdir)

    print(f'Creando directorios bajo {outdir}')
    if not os.path.exists(f"{outdir}/000"):
        for i in range(4096):
            os.mkdir(f'{outdir}/{i:03x}')
            #for j in range(256):
            #    os.mkdir(f'{outdir}/{i:02x}/{j:02x}')

    tint          = args['tint']
    noise_power_1 = args['noise1']
    noise_power_2 = args['noise2']
    blur_radius_1 = args['blur']
    noise_scale_1 = args['xscale']
    noise_scale_2 = args['yscale']
    threshold     = args['thres']
    suffix = f"t{tint}-u{threshold}-n{noise_power_1}-N{noise_power_2}-x{noise_scale_1}-y{noise_scale_2}-b{blur_radius_1}"
    ground_truth = bool(args['ground_truth'])
    quality     = float(args['min_quality'])

    
    #
    # obtenemos hojas del rollo
    #
    hojas = imgdb.get_hojas_buenas(rollo,umbral)
    nhojas = len(hojas)
    print(f"rollo:{rollo} hojas buenas:{nhojas}")
    nbloques_buenos = 0
    for hoja in hojas:
        nombre_hoja = hoja[1]
        score_hoja = hoja[-2]
        rollo_hoja = hoja[0]
        imgdir = f"{basedir}/r{rollo_hoja}/"
        print(f"hoja:{nombre_hoja} score={score_hoja}",end=" ")
        #
        # hojas com bajo score son ignoradas
        #
        if score_hoja < quality:
            print(" (descartada)")
            continue
        #
        # filtramos bloques que valen la pena
        #
        bloques = imgdb.get_bloques_buenos(nombre_hoja,minscore=1.0,minlength=2)
        #
        # cargamos hoja
        #
        clean_image = Image.open(f"{imgdir}/{nombre_hoja}.tif").convert('L')
        clean_image_array = 1.0-np.asarray(clean_image).astype(np.float)*(1.0/255.0)
        #
        # recorremos cada bloque en la hoja
        #
        nbloques = len(bloques)
        nbloques_buenos = nbloques_buenos + nbloques
        print(f" bloques buenos:{nbloques}")
        for bloque in bloques:
            #
            # ultima columna del CSV es el texto
            #
            text = bloque[12]
            print(text,end='|')
            hash_bloque = bloque[14]
            subdir1 = hash_bloque[:3]
            subdir2 = "" #hash_bloque[2:4]
            block_dir = f'{outdir}/{subdir1}/{subdir2}'
            clean_block_array = clean_image_array[bloque[6]:bloque[8],bloque[7]:bloque[9]]
            if args['ground_truth']:
                block_image = bool_array_to_pil_img(clean_block_array < 0.5)
                block_image.save(f"{block_dir}/{hash_bloque}-ORIGINAL.tif",compression="group4")
            degraded_block_array = degrade_text(clean_block_array,args).astype(np.bool)
            block_image = bool_array_to_pil_img(degraded_block_array)
            block_image.save(f"{block_dir}/{hash_bloque}-{suffix}.tif",compression="group4")
            f = open(f"{block_dir}/{hash_bloque}.txt","w")
            print(text,file=f)
            f.close()
        print('|')
        #
        # fin for file_name in file_list
        #
    print(f"total de bloques buenos {nbloques_buenos}")


