# Postprocesamiento

Procesamiento de los resultados obtenidos de LUISA. Esto incluye resumir la información ingresada por los usuarios sobre los bloques (analizar bloques), ensamblar versiones legibles de las páginas transcritas (ensamblar páginas), etc.

README.md ..................... este archivo
resumir_bloques_luisa.py ...... resume los resultados de LUISA, 
                                combinando las múltiples respuestas de cada
                                bloque en una sola decisión.
config.py ..................... configuración del sistema
data .......................... datos necesarios para el post-procesamiento
dicsearch.py .................. funciones de búsqueda eficiente en diccionarios
doc ........................... documentos del módulo
ensamblar_paginas_luisa.py .... genera imágenes con texto estimado de LUISA
exportar_luisa_a_hdf5.py ...... guarda los resultados de LUISA en HDF5
imgdb.py ...................... funciones para acceder a DB de preprocesamiento 
json_to_csv.py ................ convierte JSONs generados por LabelMe a CSV
luisadbpg2.py ................. interfaz con DB principal de LUISA (Postgres)
