# -*- coding: utf-8 -*-
import sys, os


#ROOTDIR="/home/carpani/Documentos/Facultad/csi/2016/MemoriaHistoricaLocal/imgproc/"

# --------------------------------------------------------------------------
# 2 BASE DE DATOS
# --------------------------------------------------------------------------

DB_HOST = 'localhost'
DB_USER = 'captcha'
DB_PASS = 'c4ptch4m4n'
DB_NAME = 'lu_cons'
DB_PORT = 5432
DB_RPORT= 20543

#
# --------------------------------------------------------------------------
# 2 PROCESAMIENTO
# --------------------------------------------------------------------------
#
# 2.1 Ruta de datos de entrada y subproductos directamente utilizables
#     por otras etapas (ej., imagenes reducidas, alineadas, etc.)
#
##### DIRECTORIOS

#DATADIR   = '/media/nacho/Elements/data/luisa'
DATADIR   = '/luisa'
#
# Datos originales en formato PBM, gzipeados
#
ORIGDIR   = os.path.join(DATADIR,'originales') 
#
# extension de los archivos originales
#
IMG_EXT = 'tif'
IMG_COMP = 'group4'
#
# lista de rutas de archivos a procesar, relativas a ORIGDIR
#
FILE_LIST = os.path.join(ORIGDIR, 'TODO.txt')
#
# Imagenes alineadas en tamaño original, para extraer bloques en sistema web
# Esta carpeta es copiada con el nombre img_full en el web
#
#ALIGNED_DIR = os.path.join(DATADIR,'alineadas')
ALIGNED_DIR = "/luisa/repImgs/1.hojas_alineadas/"
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
#
#
#
HASHSALT  = "dinosaurios1973"
