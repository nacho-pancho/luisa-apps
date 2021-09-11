#!/bin/bash
wget -c http://iie.fing.edu.uy/~nacho/data/luisa/episodios_nacionales.zip
unzip -o episodios_nacionales.zip
cat Epi*.txt > benito_perez_galdos_all.txt
