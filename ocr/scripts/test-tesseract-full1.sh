#!/bin/bash
for i in ${1}/*.tif
do
	tesseract --psm 13 -l spa --dpi 400 $i ${i/tif/tess} | tee tess.log
done
