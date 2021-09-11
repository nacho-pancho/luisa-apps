#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JSON_TO_CSV
Convierte la información de los jsons de una carpeta a un archivo '.csv' que puede abrirse como planilla electrónica

Version compatible con LABELME 20190901

Se supone que los .json estan codificados en utf-8
El archivo '.csv' creado tiene como separador ';' por defecto (punto y coma, semicolon en inglés). Se puede cambiar
con la opcion 'delimiter'
El archivo csv de salida se condifica en utf-8
"""


import json
import os

import argparse

# argument parser
ap = argparse.ArgumentParser(description="Convierte la información de los jsons de una carpeta a un archivo '.csv' que puede abrirse como planilla electrónica.")
ap.add_argument("json_directory", help="Carpeta donde están los json")
ap.add_argument("summary_csv_filename", help="Archivo '.csv' que guardará el resumen de los json")
ap.add_argument("-d", "--delimiter",default=';', 	help="Separador para las columnas del csv (default=';')")
ap.add_argument('-r', '--recursive', action='store_true', help="Recorrer también las sub-carpetas")
ap.add_argument('-p', '--prune_help', action='store_true', help="No cargar los textos de ayuda de tipo y origen")


args = vars(ap.parse_args())

summary_file = open(args['summary_csv_filename'], "w", encoding='utf-8')

template = '%s{0}%s{0}%s{0}%s{0}%s{0}%s{0}%s{0}%s{0}%s{0}%s\n'.format(args['delimiter'])
summary_file.write(template % ('imagen',
                               'año',
                               'mes',
                               'dia',
                               'tipo',
                               'origen',
                               'descripcion',
                               'compuesto',
                               'multihoja',
                               'graficos') )


for (rootDir, dirNames, filenames) in os.walk(args['json_directory']):
    for filename in sorted(filenames):
        (root,ext) = os.path.splitext(filename)
        if ext == '.json':
            json_fullfilename = os.path.join(rootDir, filename)

            with open(json_fullfilename, encoding='utf-8') as f:
                contents = f.read()

                
                data = json.loads(contents)

                doc_imagename = data['imagePath']
                doc_year = data['date'][0]
                doc_month = data['date'][1]
                doc_day = data['date'][2]

                doc_type = [k for (k,v) in data['flags'].items() if v ]
                doc_origin = [k for (k,v) in data['origins'].items() if v ]

                if args['prune_help']:
                    doc_type = [t.split('->')[0].strip() for t in doc_type]
                    doc_origin = [t.split('->')[0].strip() for t in doc_origin]

                #DEPRECATED en LABELME 20190901    doc_year = [k for (k,v) in data['years'].items() if v ]
                #DEPRECATED en LABELME 20190901    doc_dept = [k for (k,v) in data['departments'].items() if v ]
                #DEPRECATED en LABELME 20190901    doc_division = [k for (k,v) in data['divisions'].items() if v ]

                doc_description = data['description']
                doc_composite = [k for (k,v) in data['composites'].items() if v ]
                doc_multi = [k for (k,v) in data['multipages'].items() if v ]
                
                doc_shapes = [[s['label'],s['points']] for s in data['shapes']]

                
                summary_file.write(template % (doc_imagename,
                                              doc_year,
                                              doc_month,
                                              doc_day,
                                              doc_type,
                                              doc_origin,
                                              doc_description,
                                              doc_composite,
                                              doc_multi,
                                              doc_shapes
                                              ))


    if not args['recursive']:
        break

summary_file.close()                
                
    


