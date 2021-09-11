'''
Recorre el dataset y compara cada texto con las frases dadas en las queries
Entradas:
  dataset_dir		directorio que tiene debajo los archivos txt resultantes del tesseract
  output_dir		directorio donde se va a guardar el archivo de salida
  queries_filename	archivo con frases a buscar
  output_filename_suffix	sufijo a agregar al archivo de salida <output_dir>/<dataset_dir>_<output_filename_suffix>.csv
  verbose		imprimir a pantalla resultados intermedios como las frases encontradas y los scores
'''
import difflib
from difflib import SequenceMatcher as SM
import cv2
import matplotlib.pyplot as plt
import subprocess
import os
from PIL import Image
import pytesseract
from nltk.util import ngrams
import nltk
import codecs
import numpy as np
import argparse


# BASADO EN
# https://stackoverflow.com/questions/3788870/how-to-check-if-a-word-is-an-english-word-with-python

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset_dir", required=True,
    help="path to input dataset of tesseract text results")
ap.add_argument("-o", "--output_dir", type=str, required=True,
    help="path to output directory")
ap.add_argument("-n", "--nombre", type=str, required=True,
    help="Nombre de archivo con lista de nombres propios.")
ap.add_argument("-p", "--palabras", type=str, required=True,
    help="Nombre de archivo con lista de palabras conocidas.")
ap.add_argument("-s", "--output_filename_suffix", type=str, default = 'text_analysis',
    help="suffix for the output filename")
ap.add_argument("-v", "--verbose", action='store_true',
    help="show intermediate results")
ap.add_argument("--include_all_words", action='store_true',
    help="Include all words found in document apart from the dictionary words")


args = vars(ap.parse_args())


#
# deben ser los generados por "compilar.py" en el proyecto "diccionarios"
# https://gitlab.fing.edu.uy/mh/diccionarios
#
archivo_nombres = "nombres.txt"
archivo_palabras = "palabras.txt"
palabras = None
nombres = None

with open(args['palabras'], encoding="utf-8") as fpal:
    palabras =  set(p.lower() for p in fpal)

with open(args['nombres'], encoding="utf-8") as fnom:
    nombres =  set(n.lower() for n in fnom)

def is_name(word):
    return p in nombres

def is_valid_word(p):
    return p in palabras


validExts = (".tif.txt")
contains = None

for (rootDir, dirNames, filenames) in os.walk(args["dataset_dir"], followlinks=True):
    print('rootDir=', rootDir)
    print('dirNames=', dirNames)
    # print('fileNames=' , filenames)
    # loop over the filenames in the current directory
    txtPaths = []
    for filename in sorted(filenames):
        # print(filename)
        # if the contains string is not none and the filename does not contain
        # the supplied string, then ignore the file
        if contains is not None and filename.find(contains) == -1:
            continue
        # determine the file extension of the current file
        #ext = filename[filename.rfind("."):].lower()
        # check to see if the file is an image and should be processed
        if filename.endswith(validExts):
            # construct the path to the image and yield it
            # imagePath = os.path.join(rootDir, filename).replace(" ", "\\ ")
            txtPath = os.path.join(rootDir, filename)
            txtPaths.append(txtPath)

    numberOfDocsInRollo = len(txtPaths)
    if (numberOfDocsInRollo > 0):  # si el rollo contiene imagenes
        _, rollo_name = os.path.split(rootDir)  # rootDir.split('/')[1]

        resultFilename = os.path.join(args['output_dir'], '%s_%s.csv' % (rollo_name,args['output_filename_suffix']))

        if not os.path.isdir(args['output_dir']):
            os.makedirs(args['output_dir'])

        print('--------------------------------------------------------')
        print(rollo_name)
        print('El rollo contiene %d documentos' % numberOfDocsInRollo)
        print('result_filename =', resultFilename)
        print('--------------------------------------------------------')

        resultados = []
        resultados_numericos = []
        for txt_full_filename in txtPaths:

            _, txt_name = os.path.split(txt_full_filename)
            image_name = txt_name.rstrip('.txt')

            if True: #args['verbose']:
                print('--------------------------------------------------------')
                print(txt_full_filename)

            if not os.path.isfile(txt_full_filename):
                print('%s NOT FOUND!' % txt_full_filename)
                continue

            with open(txt_full_filename, 'r') as f:
                raw_text = f.read()



            tokens = nltk.wordpunct_tokenize(raw_text)

            text = nltk.Text(tokens)
            words = [w.lower() for w in text]
            word_is_in_dict = np.asarray( [is_valid_word(w) for w in words] )
            word_lengths = np.asarray( [len(w) for w in words] )
            correct_words = [words[i]  for i in range(len(words)) if word_is_in_dict[i]]

            if args['verbose']:
                print(len(words))
                print(len(word_set))
                print(words)
                print(word_is_in_dict)
                print('%d / %d palabras correctas' % ( sum(word_is_in_dict), len(words) ) )
                print(correct_words)

            word_count = len(words)
            short_word_count = sum( word_lengths<=3 )
            long_word_count =  sum( word_lengths >3 )

            correct_word_count = sum(word_is_in_dict)
            correct_short_word_count = sum(  np.logical_and(word_is_in_dict, word_lengths<=3) )
            correct_long_word_count =  sum(  np.logical_and(word_is_in_dict, word_lengths >3) )

            resultados_img = [image_name]
            resultados_img.append( word_count )
            resultados_img.append( short_word_count )
            resultados_img.append( long_word_count )

            resultados_img.append( correct_word_count )
            resultados_img.append( correct_short_word_count )
            resultados_img.append( correct_long_word_count )

            resultados_img.append('%.2f' % ( correct_word_count / (word_count + 0.001) )  )
            resultados_img.append('%.2f' % ( correct_long_word_count / (long_word_count + 0.001)))

            resultados_img.append( str(correct_words) )
            if args['include_all_words']:
                resultados_img.append( str(words) )

            resultados.append(resultados_img)


        if args['verbose']:
            print(resultados)

        np.savetxt(resultFilename, resultados, delimiter=';', fmt='%s')

