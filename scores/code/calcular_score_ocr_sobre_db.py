#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Este programa corre el score desarrollado (vecscore con pesos ajustados por transcripción
manual) sobre una lista de archivos --list en el directorio --datadir.
Los scores son guardados en un archivo de salida 'vecscore_results.txt' formateados como
diccionario.
@author: lagorio
"""
# ---- importacion de paquetes necesarios --------------------------------------------#
# ---- notar que scores importa muchas bibliotecas más -------------------------------#
import os.path
import argparse
import scores
import subprocess
import sqlite3 as db

# ------------------------------------------------------------------------------------#
if __name__ == '__main__':
    ######################## ARGUMENTOS DE LINEA DE COMANDOS #########################
    ##### datadir = donde están los archivos, list = lista de archivos a scorear #####
    ##################################################################################
    ap = argparse.ArgumentParser()
    ap.add_argument("-r", "--rootdir", type=str, default="/datos/luisa",
                    help="root dir for LUISA files")
    ap.add_argument("-i", "--imgdir", type=str, default="originales",
                    help="path prefix  where to find files, relative to basedir")
    ap.add_argument("-d", "--dbdir", type=str, default="db",
                    help="path prefix  where to find files, relative to basedur")
    ap.add_argument("-D", "--dbfile", type=str, default="test.db",
                    help="Sqlite3 database files where transcription info is stored")
    ap.add_argument("-o", "--outdir", type=str, default="by-score",
                    help="output directory for classified images.")
    ################################# INICIALIZACIÓN #################################
    args = vars(ap.parse_args())
    print(args)
    root_dir = args["rootdir"]
    img_dir  = args["imgdir"]
    db_dir   = args["dbdir"]
    out_dir  = args["outdir"]
    db_fname = args["dbfile"]
    ocr_points = []
    if not os.path.exists(root_dir):
        print(f'ERROR: directorio base {root_dir} no existe')
        exit(1)

    if img_dir[0] != '/':
        img_dir = os.path.join(root_dir,img_dir)
    if not os.path.exists(img_dir):
        print(f'ERROR: directorio de imagenes {img_dir} no existe')
        exit(1)
    
    if db_dir[0] != '/':
        db_dir = os.path.join(root_dir,db_dir)
    if not os.path.exists(db_dir):
        print(f'ERROR: directorio de base de datos {db_dir} no existe')
        exit(1)


    if db_fname[0] != '/':
        db_fname = os.path.join(db_dir,db_fname)
    if not os.path.exists(db_fname):
        print(f'ERROR: archivo de base de datos {db_fname} no existe')
        exit(1)

    if out_dir[0] != '/':
        out_dir = os.path.join(root_dir,out_dir)
    if not os.path.exists(out_dir):
        print(f'Creando directorio {out_dir}')
        os.makedirs(out_dir)
    
    minval = 1
    maxval = 16
    with db.connect(db_fname) as db_conn:
        db_cursor = db_conn.cursor()
        nimage = 0
        res = db_cursor.execute('SELECT nombre,ocrtext FROM image ORDER BY nombre')
        image_data = [ r for r in res.fetchall() ] # deep copy
        query = "ALTER TABLE image ADD COLUMN  "
        i = minval
        while i <= maxval:
            db_cursor.execute(f"ALTER TABLE image ADD COLUMN n{i} integer") 
            db_cursor.execute(f"ALTER TABLE image ADD COLUMN v{i} integer") 
            i += 1
        db_conn.commit()
        db_cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS image_index ON image (nombre)")
        db_conn.commit()
        for row in image_data:
            rel_fname = row[0]
            ocr_text  = row[1]
            nimage = nimage + 1    # proxima imagen
            # nombres de archivos y directorios de entrada y salida
            rel_dir,fname = os.path.split(rel_fname)
            fbase, fext    = os.path.splitext(fname)
            relbase, _ = os.path.splitext(rel_fname)
            
            #
            # compute scores
            #
            ocr_score,features = scores.score_auto_2(ocr_text,return_features=True)
            ocr_score = int(100*ocr_score)
            #
            # update DB
            #
            query = 'UPDATE image SET ocrscore=? WHERE nombre=?'
            print(f'UPDATE image SET ocrscore={ocr_score} WHERE nombre="{rel_fname}"')
            try:
                db_cursor.execute(query,(ocr_score,rel_fname))
            except:
                print('ERROR al actualizar db')
                exit(2)
            #
            # feature list
            #
            query = "UPDATE image SET"
            fields = "( "
            values = "( "
            i = minval
            while i < maxval:
                fields += f"n{i}, v{i}, " 
                values += f"?, ?, "
                i += 1
            fields += f"n{i}, v{i} )" 
            values += f"?, ? )"
            query += fields + " = "  + values + " WHERE nombre=?"
            #print(query)
            features.append(rel_fname)
            db_cursor.execute(query,features)
             #
            # create link to files
            #
            percent_score = 10*int(ocr_score/10)
            pdir = f'{percent_score:02d}'
            findir = os.path.join(img_dir,rel_dir)
            fimgin = os.path.join(findir,fbase + '.tif')
            foutdir = os.path.join(out_dir,pdir,rel_dir)
            if not os.path.exists(foutdir):
                os.makedirs(foutdir)
            fimgout = os.path.join(foutdir,fbase + '.tif')
            command = f'ln {fimgin} {fimgout}'
            #command = f'cp -u {fimgin} {fimgout}'
            subprocess.call(command, shell=True)
            if (nimage//100)*100 == nimage:
                db_conn.commit()
        db_conn.commit()
