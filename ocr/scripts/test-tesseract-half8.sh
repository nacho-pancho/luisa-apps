#!/bin/bash
for i in ${1}/*.tif
do
	tesseract --psm 13 -l spa --dpi 150 $i ${i/tif/tess} > /dev/null
done
