#!/bin/bash
pip3 install unireedsolomon
./escribir_marca.py prueba.tif -n "Cococho Peluffo" -c 12345678 -o "Cambalache Inc." coco.tif
./leer_marca.py coco.tif
display watermark.tif
echo COLOR

./escribir_marca.py prueba_color.png -n "Cococho Peluffo" -c 12345678 -o "Cambalache Inc." cocolor.tif
./leer_marca.py cocolor.tif
display watercolor.tif