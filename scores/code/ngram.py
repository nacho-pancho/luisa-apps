#!/usr/bin/env python3
#-*- coding:utf-8 -*-
#########################################################################
#
# Funciones para calcular scores de transcripciones.
#
##########################################################################
#
import pickle                  # serializacion de objetos (modelos en este caso)
import os                      # manejo de archivos
import nltk                    # para parsear texto (pip3 install nltk)
import nltk.lm.preprocessing as nlpre
import nltk.lm               as nlmodel
import math

#from nltk.util import bigrams
#from nltk.util import everygrams
#from nltk.util import sent_tokenize, word_tokenize, ngrams
#from nltk.lm.preprocessing import pad_both_ends
#from nltk.lm.preprocessing import flatten
from nltk.tokenize import RegexpTokenizer

#------------------------------------------------------------------------------

NGRAM_CORPUS   = "../data/benito_perez_galdos_all.txt"

#------------------------------------------------------------------------------

def get_corpus(corpus_file):
    '''
    bajar un corpus de texto
    '''
    # Text version of https://kilgarriff.co.uk/Publications/2005-K-lineer.pdf
    if os.path.isfile(corpus_file):
        with open(corpus_file, "r",encoding='utf8') as fin:
            text = fin.read()
        return text
    else:
        print("ERROR: falta descargar corpus. ")
        return None

#------------------------------------------------------------------------------

def sent_tokenize(texto):
    '''
    Separa texto en oraciones.
    '''
    if sent_tokenize.st is None:
        try:
            sent_tokenize.st = nltk.data.load('tokenizers/punkt/spanish.pickle')
        except:
            nltk.download("punkt")
            sent_tokenize.st = nltk.data.load('tokenizers/punkt/spanish.pickle')
    return sent_tokenize.st.tokenize(texto)
sent_tokenize.st = None

#------------------------------------------------------------------------------

def word_tokenize(text):
    '''
    Separa una oración en palabras.
    '''
    tokenizer = RegexpTokenizer('\w+|\$[\d\.]+|\S+')
    return tokenizer.tokenize(text)
    #return nltk.tokenize.word_tokenize(frase)

#------------------------------------------------------------------------------

MODEL_FILE = "laplace.pickle"
MODEL_ORDER = 2 # bigramas,Markov de orden 1

#------------------------------------------------------------------------------

def get_model():
    '''
    Entrena un modelo de tipo n-gramas
    basado en un corpus predeterminado y un 
    orden prefijado. 
    (ver la configuración global de este módulo)
    '''
    if get_model.__model is not None:
        return get_model.__model

    if os.path.exists(MODEL_FILE):
        print("Cargando modelo")
        f = open(MODEL_FILE,"rb")
        get_model.__model = pickle.load(f)
        f.close()
        return get_model.__model

    print("Aprendiendo modelo.")
    corpus = get_corpus(NGRAM_CORPUS)
    '''
    Entrenamiento de modelo n-grams usando las funciones de NLTK
    Basado en https://www.kaggle.com/alvations/n-gram-language-model-with-nltk
    '''
    padded_corpus = nlpre.pad_both_ends(corpus,n=MODEL_ORDER)
    #
    # separa frases y luego palabras.
    #
    tokenized_text = [list(map(str.lower, word_tokenize(sent))) 
                        for sent in sent_tokenize(corpus)]
    #
    # el "pipeline" hace varias cosas:
    # - agrega paddings a los lados para un modelo de n-gram del orden deseado
    # - "achata" el texto, juntando las palabras de las frases (sentences)
    # - crea un "vocabulario" de palabras conocidas con lo que encuentra
    #
    train_data, padded_sents = nlpre.padded_everygram_pipeline(MODEL_ORDER, tokenized_text)
    #
    # entrenamos un modelo probabilístico utilizando regularización de Laplace,
    # esto es, si se observaron m n-grams, hay q n-gramas distintos y la frecuencia de ocurrencia de 
    # un n-grama dado es f, entonces la probabilidad estimada de ese n-grama es p = (f+1)/(m+q)
    #
    get_model.__model = nlmodel.Laplace(MODEL_ORDER)
    get_model.__model.fit(train_data, padded_sents)
    f = open(MODEL_FILE,"wb")
    pickle.dump(model,f)
    f.close()
    return get_model.__model 

get_model.__model = None

#------------------------------------------------------------------------------

def bigram_score(context,word):
    model = get_model()
    #lsp  = score_ngram.model.logscore(palabra,context=frase[i-1].split())
    nc    = model.counts[ context ]
    np    = model.counts[ [context] ][ word ]
    #if debug:
    #    print(f"\t\t{palabra:20s} nc {nc:8d} np {np:8d} score {lkt:12.6f}")
    a     = 300000 # aprox number of possible words
    pkt   = (np+(1.0/a))/(nc+1.0)
    return math.log2(pkt)


#------------------------------------------------------------------------------

def text_score(texto,debug=False,max_lev_dist=0):
    '''
    Calcula la verosimilitud de un texto
    utilizando un modelo tipo n-gram con
    n = 3 (a.k.a., un modelo Markov de orden 2).
    El modelo es entrenado sobre un corpus fijo.
    Para calcular la verosimilitud de palabras
    no encontradas en el corpus se sustituye dichas
    palabras por un comodín especial.

    En particular, se sustituyen los nombres y apellidos
    conocidos por '<nombre>' y '<apellido>' de modo
    de independizar al modelo de ese tipo de particularidades.

    '''
    #print("Score trigramas...")
    #
    # obtenemos modelo utilizado para evaluar transcripcion
    #
    model = get_model()
    #
    # convertimos texto a minúscula
    #
    texto = texto.lower()
    #
    # tokenizar: convertir texto en lista de frases
    #
    frases = sent_tokenize(texto)
    #
    # convertir frases en listas de palabras
    #
    frases = [ word_tokenize(frase) for frase in frases ]
    #
    # TODO: sustituir palabras con 1 error sitactico por su mas parecida en una lista
    #
    #
    # agregar relleno (padding) al ppio de cada frase de modo de poder
    # tener una secuencia de inicio para evaluar las probabilidades
    # 
    frases_con_pad = [ nltk.pad_sequence(frase, pad_left=True, left_pad_symbol="<s>", 
                                pad_right=False, n=MODEL_ORDER) for frase in frases ]

    # TODO: eliminar basura
    # TODO: sustituir nombres y apellidos en el texto
    # TODO: sustituir siglas en el texto 
    logscore = 0
    npal = 0
    nlet = 0
    for frase0 in frases_con_pad:
        lsf = 0
        frase = [f for f in frase0]
        if not len(frase):
            continue
        if debug:
            print('FRASE:\n',frase)
        for i in range(MODEL_ORDER-1,len(frase)): 
            contexto = frase[i-1]
            palabra = frase[i] 
            lkt = bigram_score(contexto,palabra)
            lsf += lkt
            npal += 1
            nlet += len(palabra)
            mlsf = lsf/len(frase)
        if debug:
            print(f"\taccu\t{lsf:12.6f} mean\t{mlsf:12.6f}\n")
        logscore += mlsf
    return logscore/len(list(frases_con_pad))

#------------------------------------------------------------------------------

if __name__ == "__main__":
    #
    # test
    #
    texto = "en la casa de mi hermana hay dos perros"
    print("SCORE:",text_score(texto,debug=True))
    texto = "en la casa de mi hermana hay dos cerros"
    print("SCORE:",text_score(texto,debug=True))
    texto = "en la perro de mi cuatro hay casa perros"
    print("SCORE:",text_score(texto,debug=True))

    #muestras = ('no_texto','texto_malo','texto_bueno','texto_muy_bueno')
    muestras = list()
    for m in muestras:
        print('---------',m,'---------')
        f = open(f'../data/{m}.txt')
        texto = f.read()
        f.close()
        print("SCORE:",text_score(texto,debug=True))

