# -*- coding: utf-8 -*-
import os

ROOTDIR="/luisa"

WEBDIR = ROOTDIR + "www"
#
# --------------------------------------------------------------------------
# NO EDITAR DE AQUI EN MAS!
# --------------------------------------------------------------------------
#
#
# --------------------------------------------------------------------------
# 2 PROCESAMIENTO
# --------------------------------------------------------------------------
#
# 2.1 Ruta de datos de entrada y subproductos directamente utilizables
#     por otras etapas (ej., imagenes reducidas, alineadas, etc.)
#
##### DIRECTORIOS
DIC = ROOTDIR + "../dic/diccionario.txt"

DATADIR   = ROOTDIR # os.path.join(ROOTDIR,"datos")
#
# 2.1.1 Datos originales en formato PBM, gzipeados
#
ORIGDIR   = os.path.join(DATADIR,'originales') 
#
# 2.1.1 Datos originales en formato PBM, gzipeados
#
LISTDIR   = os.path.join(DATADIR,'listas') 
#
# 2.1.2 extension de los archivos originales
#
EXT = '.tif'
COMP='group4'
#
# 2.1.3 lista de rutas de archivos a procesar, relativas a ORIGDIR
#
FILE_LIST = ORIGDIR + 'IMAGENES.txt'
REEL_LIST  = ORIGDIR + 'ROLLOS.txt'
#
# 2.1.4 Imagenes reducidas. La estructura interna de directorios es idéntica a lo que 
#       se encuentra dentro de ORIGDIR
#
DISCARDED_DIR  = os.path.join(DATADIR,'descartadas')
#
# 2.1.5 Imagenes alineadas en tamaño original, para extraer bloques en sistema web
#       Esta carpeta es copiada con el nombre img_full en el web
#
ALIGNED_DIR = os.path.join(DATADIR,"alineadas")
#
# 2.1.6 Imagenes alineadas y reducidas, para extraccion de bloques y otras etapas
#       internas de procesamiento
#
#
# 2.2 Ruta para almacenar resultados intermedios del procesamiento (metadata, etc.)
#
RESDIR = os.path.join(DATADIR,'results')
#
# 2.3 Metadata de alineacion
#
ALIGNED_META_DIR = ALIGNED_DIR
#
# 2.4 Metadata de análisis para clustering y para extraer bloques
#
ANALYSIS_DIR = ALIGNED_DIR
#
# aqui se guardan las coordenadas de los bloques extraidos y filtrados 
#
BLOQUES_DIR = ALIGNED_DIR
#
# 2.5 parametros de alineado
#
#
# 2.5.1 ancho del kernel utilizado para alinear
#
ANCHO_KERNEL = 250 # ancho del kernel
#
# 2.5.1 angulo maximo admisible de inclinacion (para ambos lados)
#
ANG_MAX = 5
#
# 2.5.2 resolucion de angulo en la alineacion
#
ANG_STEP = 0.5
#
# altura de la grilla utilizada para chequear alineacion
#
GRID_STEP_Y = 4
#
# ancho de la grilla utilizada para chequear alineacion
#
GRID_STEP_X = 16
#
# todo bloque con menos de este porcentaje de pixeles negros
# no se utiliza en la alineacion
#
USABLE_PATCH_THRES=0.025
#
# margen a recortar del lado izquierdo de las img. originales
#
MARGIN_LEFT=200
#
# margen superior a recortar de las img. originales
#
MARGIN_TOP=200
#
# altura de la imagen final luego del recorte
#
PAGE_HEIGHT=4500
#
# ancho de la imagen luego del recorte
#
PAGE_WIDTH=3400 
#
# esscala utilizada para el análisis (esto determina el tamanio
# de las imagenes reducidas arriba)
#
SCALE = 0.25
# --------------------------------------------------------------------------
# DB 
# --------------------------------------------------------------------------
HASHSALT  = u"dinosaurios1973"
#
# 1.1 BASE DE DATOS SQLITE3
# 
DB_FILENAME    = os.path.join(DATADIR,"/microfilm.db")
#

