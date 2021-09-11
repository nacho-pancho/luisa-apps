#-*- coding:utf-8 -*-
#########################################################################
#
# Funciones para calcular scores de transcripciones.
#
##########################################################################
#
import math
import io                      # I/O standard
import pickle                  # serializacion de objetos (modelos en este caso)
import os                      # manejo de archivos
import nltk                    # para parsear texto (pip3 install nltk)
import nltk.lm.preprocessing as nlpre
import nltk.lm               as nlmodel

from bisect import bisect_left # para busqueda en lista ordenada
import dicsearch               # archivo local
import numpy as np

import textdistance
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
        with io.open(corpus_file, encoding='utf8') as fin:
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

def train_ngram_model():
    '''
    Entrena un modelo de tipo n-gramas
    basado en un corpus predeterminado y un 
    orden prefijado. 
    (ver la configuración global de este módulo)
    '''
    if os.path.exists(MODEL_FILE):
        print("Aprendiendo modelo")
        f = open(MODEL_FILE,"rb")
        model = pickle.load(f)
        f.close()
        return model

    #print("Cargando corpus.")
    corpus = get_corpus(NGRAM_CORPUS)
    #print("Entrenando modelo de n-gramas...")
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
    model = nlmodel.Laplace(MODEL_ORDER)
    model.fit(train_data, padded_sents)
    f = open(MODEL_FILE,"wb")
    pickle.dump(model,f)
    f.close()
    return model 

#------------------------------------------------------------------------------

def score_ngram(texto,debug=False,max_lev_dist=0):
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
    if score_ngram.model is None:
        score_ngram.model = train_ngram_model()
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
            # 
            # calculo a mano da exactamente igual
            #
            nc = score_ngram.model.counts[ contexto ]
            np = score_ngram.model.counts[ [contexto] ][ palabra]
            #
            # Kirchevskii-Trofimov (KT)
            #a = len(score_ngram.model.vocab)
            # pL = (np+1)/(nc+a)
            # menos suave que KT: 
            a = 2**64
            pkt = (np+(1.0/a))/(nc+1)
            lkt = math.log2(pkt)
            #print(nc,np,a,pkt,lkt)
            #lsp = score_ngram.model.logscore(palabra,context=frase[i-1].split())
            if debug:
                print(f"\t\t{palabra:20s} nc {nc:8d} np {np:8d} score {lkt:12.6f}")
            #lsf += lsp
            lsf += lkt
            npal += 1
            nlet += len(palabra)
            mlsf = lsf/len(frase)
        if debug:
            print(f"\taccu\t{lsf:12.6f} mean\t{mlsf:12.6f}\n")
        logscore += mlsf
    return logscore/len(list(frases_con_pad))
#
# miembro estático de función score_ngram
#
score_ngram.model = None

#------------------------------------------------------------------------------

def palabras(texto,min_largo):
    '''
    Remaxlen sencillo de palabras; versión pobre de word_tokenize
    '''
    # split: corta texto en espacios
    # strip: quita símbolos de los bordes
    # replace: quitamos los puntos dentro de una misma palabra
    # de todos modos, lo mejor sería usar un tokenizador más profesional que esto
    #
    palabras = [s.strip(' \n\t\b\r!#$%&/()=?¿¡*+[]{};:,.-_<>|°').replace('.','').lower() for s in texto.split()]
    return list(filter(lambda x: len(x) >= min_largo, palabras))

#------------------------------------------------------------------------------

def score_simple(texto,min_largo=4):
    '''
    Dado un texto, devuelve la fracción de palabras de un cierto 
    largo mínimo que están presentes en el diccionario global 
    del módulo.
    '''
    lista_de_palabras = palabras(texto,min_largo)
    num_palabras =  len(lista_de_palabras)
    if num_palabras == 0:
        return 0
    num_palabras_validas = 0
    for p in lista_de_palabras:
        if approx_match(p,0):
            num_palabras_validas += 1
    return num_palabras_validas/num_palabras

#------------------------------------------------------------------------------

def score_dist_uno(texto,min_largo=4):
    '''
    Dado un texto, devuelve la fracción de palabras de un cierto 
    largo mínimo que a lo sumo a distancia 1 de algún elemento
    del diccionario.
    '''
    lista_de_palabras = palabras(texto,min_largo)
    num_palabras =  len(lista_de_palabras)
    if num_palabras == 0:
        return 0
    numbuenas=0
    for pal in lista_de_palabras:
        numbuenas += (len(dicsearch.search(pal, 1))>0)
    return numbuenas / num_palabras

#------------------------------------------------------------------------------

# def score_dist_uno_exp(texto,min_largo=4):
#     '''
#     Ni idea para qué usamos esto
#     '''
#     return 10*10**score_dist_uno(texto,min_largo)

# #------------------------------------------------------------------------------

# def is_valid_word(word, valid_words):
#     '''
#     Búsqueda simple de una palabra en un conjunto
#     '''
#     return word in valid_words

#------------------------------------------------------------------------------

# def true_score(ocr_text, manual_text, min_largo = 4):
#     listado_ocr = palabras(ocr_text, min_largo)
#     listado_man = palabras(manual_text, min_largo)
#     num_ocr = len(listado_ocr)
#     numbuenas=0
#     for pal in listado_ocr:
#         if is_valid_word(pal, listado_man):
#             numbuenas += 1
#     return numbuenas / num_ocr

# #------------------------------------------------------------------------------

# def true_score_exp(ocr_text, manual_text, min_largo = 4):
#     listado_ocr = palabras(ocr_text, min_largo)
#     listado_man = palabras(manual_text, min_largo)
#     num_ocr = len(listado_ocr)
#     #num_man = len(listado_man)
#     numbuenas=0
#     for pal in listado_ocr:
#         if is_valid_word(pal, listado_man):
#             numbuenas += 1
#     return 10*10**(numbuenas / num_ocr)

#------------------------------------------------------------------------------

def group_by_length(listado, minlen, maxlen): 
    '''
    Agrupa las palabras en 'listado' según su largo.
    Se descartan todas las que tengan largo menor a minlen
    Todas las que tienen largo mayor o igual a 'maxlen'
    van al mismo grupo.
    '''
    vec = list()
    i = 0
    l = minlen
    while l < maxlen:
        aux = [pal for pal in listado if len(pal) == l]
        vec.append(aux)
        i += 1
        l += 1
    aux = [pal for pal in listado if len(pal) >= l]
    vec.append(aux)
    return vec

#------------------------------------------------------------------------------

def vec_score_raw(ocr_text, minlen, maxlen, tol = 0 ):
    '''
    devuelve un vector (v_minlen,v_2,...,v_maxlen) 
    donde v_i es la fracción de palabras en 'ocr_text' de largo i
    que están en el diccionario.
    '''
    listado_ocr = palabras(ocr_text, minlen)
    words_by_len = group_by_length(listado_ocr,minlen,maxlen)
    vec_scores = []
    for i in range(len(words_by_len)):
        palabras_largo_i = words_by_len[i]
        num_palabras = len(palabras_largo_i)
        num_buenas = 0
        for pal in palabras_largo_i:
            num_buenas += (len(dicsearch.search(pal, tol)) > 0)
        vec_scores.append(num_palabras)
        vec_scores.append(num_buenas)
    return vec_scores

#------------------------------------------------------------------------------

def vec_score(vec_scores_raw ):
    vec_scores = list()
    for i in range(0,len(vec_scores_raw),2):
        ni = vec_scores_raw[i]
        vi = vec_scores_raw[i+1]
        if ni > 0:
            vec_scores.append(vi/ni)
        else:
            vec_scores.append(0)
                        
    vec_scores.append(1) # agregamos un término de sesgo
    return vec_scores

#------------------------------------------------------------------------------

def vec_score_0(ocr_text, minlen, maxlen, tol = 0 ):
    '''
    (nota: no se está usando)
    devuelve un vector (v_1,v_2,...,v_maxlen) 
    donde v_i es la fracción de palabras en 'ocr_text' de largo i
    que están en el diccionario.
    '''
    listado_ocr = palabras(ocr_text, 0)
    vectorizado = group_by_length(listado_ocr,minlen,maxlen)
    vec_scores = []
    for i in range(len(vectorizado)):
        lista_de_palabras = vectorizado[i]
        num_palabras = len(lista_de_palabras)
        if num_palabras != 0:
            numbuenas = 0
            for pal in lista_de_palabras:
                numbuenas += (len(dicsearch.search(pal, 0)) > 0)
            vec_scores.append(numbuenas)
        else:
            vec_scores.append(0)
    return vec_scores/np.maximum(1e-5,np.linalg.norm(vec_scores))


#------------------------------------------------------------------------------

def score_auto_1(ocr_text):
    '''
    Primer versión de score automático 
    '''
    minlen = 2
    maxlen = 12
    #
    # de minlen a maxlen inclusive son (maxlen - minlen +1) = 11 elementos
    # se le agrega el sesgo (constante 1 al final)
    # eso da un vector de pesos de largo 12
    #
    weights = [6.71794265e-04, 1.76385566e-02, 6.66443825e-02, 0.00000000e+00, 
        3.07970924e-04, 1.40970289e-01, 3.17513298e-01, 1.73482655e-01,
        3.05009019e-03, 5.07199194e-02, 7.38124366e-02, 0.00000000e+00]
    vec_scores = vec_score(ocr_text,0,maxlen)
    vec_scores.append(1) # agregamos un término de sesgo
    return np.dot(np.array(vec_scores),np.array(weights))


def score_auto_2(ocr_text, return_features = False):
    '''
    Segunda versión.
    Interesante: la regresión le da peso 0 a las de largo 1 automáticamente,
    como era de esperar.
    '''
    minlen = 1
    maxlen = 16
    #
    # de minlen a maxlen inclusive son (maxlen - minlen +1) = 15 elementos
    # se le agrega el sesgo (constante 1 al final)
    # eso da un vector de pesos de largo 16
    #
    weights = [
        0.0,
        5.43324585e-03, 6.99707727e-03, 8.47752495e-02, 0.00000000e+00,
        1.28198871e-04, 9.70167092e-02, 3.13900864e-01, 1.44741267e-01,
        5.15433915e-03, 3.34949998e-02, 1.96877291e-02, 9.16256250e-02,
        1.73071534e-02, 4.47329265e-02, 2.07158182e-01, 0.00000000e+00 ]

    vec_scores_raw = vec_score_raw(ocr_text,minlen,maxlen)
    vec_scores = vec_score(vec_scores_raw)
    # we don't need a lot of precision
    # 0 to 100 is more than enough
    raw_score = np.dot(np.array(vec_scores),np.array(weights))
    if return_features:
        return raw_score,vec_scores_raw
    else:
        return int(raw_score*100)



#------------------------------------------------------------------------------

def tra_dist(ocr_text, manual_text):
    '''
    Dado un texto transcrito por OCR,
    y una transcripción manual (asumida como buena),
    devuelve la distancia de Levenshtein entre ambas traducciones
    '''
    listado_ocr = palabras(ocr_text, 0)
    listado_man = palabras(manual_text, 0)
    #lcs = textdistance.lcsstr.normalized_similarity(listado_ocr, listado_man)
    lcs = 0
    lev = textdistance.levenshtein.normalized_similarity(listado_ocr,listado_man)
    return lcs, lev
#------------------------------------------------------------------------------

if __name__ == "__main__":
    #
    # test
    #
    texto = "en la casa de mi hermana hay cuatro perros"
    print("SCORE:",score_ngram(texto,debug=True))

    muestras = ('no_texto','texto_malo','texto_bueno','texto_muy_bueno')
    #muestras = list()
    for m in muestras:
        print('---------',m,'---------')
        f = open(f'../data/{m}.txt')
        texto = f.read()
        f.close()
        print("SCORE:",score_ngram(texto,debug=True))

