#!/usr/bin/python3
# -*- coding:utf-8 -*-
import sys

fjson = open(sys.argv[1],'r')
json_hashes = { r.strip().split('|')[0]:r.strip().split('|')[1] for r in fjson }
fjson.close()
print('Imagenes a buscar:',len(json_hashes.keys()))

forig = open(sys.argv[2],'r')
orig_hashes = { r.strip().split('|')[0]:r.strip().split('|')[1] for r in forig }
forig.close()
print('Imagenes en repositorio:',len(orig_hashes.keys()))
jk = set(json_hashes.keys())
ok = set(orig_hashes.keys())
N  = len(jk)
Nf = 0
for i in jk:
    ji = json_hashes[i]
    if i in ok:
        Nf += 1
        jo = orig_hashes[i]
        print(f'{ji:64s} | {jo:64s}')
    else:
        print(f'{ji:64s} | ???')
