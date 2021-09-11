#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
Toma la lista de textos transcriptos por Tesseract para cada imagen (300.aplicar_ocr_a_bloques.py)
y determina qué tan legible es una imagen a partir del porcentaje de textos transcriptos que
se encuentran en un diccionario de palabras válidas.

Entradas:
  dataset_dir		directorio que tiene debajo los archivos txt resultantes del tesseract
  output_dir		directorio donde se va a guardar el archivo de salida
  queries_filename	archivo con frases a buscar
  output_filename_suffix	sufijo a agregar al archivo de salida <output_dir>/<dataset_dir>_<output_filename_suffix>.csv
  verbose		imprimir a pantalla resultados intermedios como las frases encontradas y los scores
'''
import os                      # manejo de archivos
import nltk                    # para parsear texto (pip3 install nltk)
import codecs                  # para manejar codificaciones de caracteres
import argparse                # para procesar linea de comandos
from bisect import bisect_left # para busqueda en lista ordenada
import dicsearch               # archivo local
import imgdb

#==============================================================================
# CONSTANTES

DIC_FILE="../data/diccionario_aumentado.txt"
BAD_WORDS_FILE="bad_words.txt"

#==============================================================================
# FUNCIONES

def exact_match(lst, item):
    """ efficient `item in lst` for sorted lists """
    # if item is larger than the last its not in the list, but the bisect would
    # find `len(lst)` as the index to insert, so check that first. Else, if the
    # item is in the list then it has to be at index bisect_left(lst, item)
    return (item <= lst[-1]) and (lst[bisect_left(lst, item)] == item)

def approx_match(lst,item):
    #return dicsearch.search(item,dist)
    if exact_match(lst,item):
        return True
    elif item[-1] == 's':
        if exact_match(lst,item[:-1]):
            return True
        elif exact_match(lst,item[:-2]):
            return True


def singular(palabra):
    if palabra[-1] == 's':
        return palabra
    elif palabra[-1] in ('a','e','i','o','u'):
        return palabra + 's'
    else:
        return palabra + 'es'

#==============================================================================
# MAIN

if __name__ == '__main__':

    #
    # procesamiento de linea de comandos usando argparse
    #
    ap = argparse.ArgumentParser()
    ap.add_argument("-r", "--rollo",
        help="rollo a procesar (por defecto todos los rollos)")
    ap.add_argument("-H", "--hoja", 
        help="hoja a procesar (por defecto todas en el rollo)")
    ap.add_argument("-w", "--write", 
        help="escribir resultados a base de datos")
    args = vars(ap.parse_args())
    bad_words_file = open(BAD_WORDS_FILE,"w")

    #
    # levantamos palabras del diccionario
    #
    with open(DIC_FILE, encoding="utf-8") as word_file:
        valid_words = set(word.strip().split(sep=' \n\t\r')[0].lower() for word in word_file)
    valid_words = sorted(valid_words)
    #print('valid words:',len(valid_words))

    rollo = args['rollo']
    if rollo is None:
        print('Todos los rollos')
    #
    # obtenemos hojas del rollo
    #
    hojas = imgdb.get_hojas(rollo)
    nhojas = len(hojas)
    #print(f"rollo:{rollo} hojas:{nhojas}")
    for hoja in hojas:
        nombre_hoja = hoja[1]
        score_hoja = hoja[-2]
        print(f"hoja:{nombre_hoja} score:{score_hoja}",end="")
        if score_hoja > 0:
            print(" (ya calculado)")
            continue

        bloques = imgdb.get_bloques(nombre_hoja)
        
        total_words_in_dict = 0
        total_words = 0
        good_words = list()
        bad_words =list()
        nbloques = len(bloques)        
        print(f" bloques:{nbloques}")
        for bloque in bloques:
            #
            # ultima columna del CSV es el texto
            #
            text = bloque[12]
            hash_bloque = bloque[14]
            if text is None:
                continue
            #
            # separamos texto por espacios
            #
            tokens = nltk.wordpunct_tokenize(text)
            text_parts = nltk.Text(tokens)
            #
            # nos quedamos con palabras de 4 o más caracteres
            #
            words = list(map(lambda w: w.lower().strip(' .,;:\'"[]{}-=+()*&%$#!/\\|¿?¡!"'), text_parts))
            words = list(filter( lambda w: len(w) > 0, words ))
            #
            # si no hay, pasamos al siguiente bloque
            #
            if len(words) == 0:
                continue
            words4 = list(filter( lambda w: len(w) >= 4, words ))
            #
            # buscamos cuales palabras estan en el diccioario
            #
            words_in_dict = list(filter( lambda w: approx_match(valid_words,w) or w.isnumeric(), words ))
            words4_in_dict = list(filter( lambda w: len(w) >= 4, words_in_dict ))
            
            if len(words_in_dict) > 0:
                good_words.append(words_in_dict)
                
            words_not_in_dict = list(filter( lambda w: w not in words_in_dict, words ))
            if len(words_not_in_dict) > 0:
                bad_words.append(words_not_in_dict)
                for bw in words_not_in_dict:
                    print(bw,file=bad_words_file)

            total_words = total_words + len(words)
            total_words_in_dict = total_words_in_dict + len(words_in_dict)
            if len(words) > 0:
                block_score = len(words_in_dict) / len(words)
            else:
                block_score = 0
            imgdb.update_block_score(hash_bloque,block_score)
        print(nombre_hoja,"|",total_words,"|",total_words_in_dict,"|",end=" ")
        #
        # subir cambios a db
        #
        if total_words > 0:
            score = total_words_in_dict/total_words
        else:
            score = 0
        imgdb.update_hoja_score(nombre_hoja,score)
        imgdb.commit()
        print(score)

        #
        # fin for file_name in file_list
        #
    #
    # fin with open(file_list)
    #
    bad_words_file.close()

