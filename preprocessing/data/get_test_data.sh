#!/bin/bash
wget -c http://iie.fing.edu.uy/~nacho/luisa/microfilm_test.tar.gpg 
gpg --batch --decrypt --passphrase dinosaurios microfilm_test.tar.gpg | tar x
