#!/bin/bash
mkdir -p img
wget -c  http://iie.fing.edu.uy/~nacho/luisa/microfilm_primeras_163_img.7z
#unzip -d img *.zip
7zr x *img.7z
