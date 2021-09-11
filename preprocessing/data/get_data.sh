#!/bin/bash
wget -c http://iie.fing.edu.uy/~nacho/luisa/microfilm.tar.gpg 
gpg --decrypt microfilm.tar.gpg | tar x
