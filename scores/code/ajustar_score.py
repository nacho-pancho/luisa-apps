#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Este programa toma un conjunto de posibles scores de calidad de OCR y los coteja
contra la calidad percibida por un humano.
Para eso se toman 50 imagenes clasificadas manualmente en 5 calidades (1 peor, 5 mejor)
y se comparaa esas calidades manuales con cada score candidato.
La idea es que un score va a ser mejor mientras más se correlacione con la calidad percibida.

@author: nacho
"""
#
# # paquetes base de Python3 (ya vienen con Python)
#
# import os
import os.path
import sys
import argparse
import scores
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
import sklearn.linear_model as lm

# ---------------------------------------------------------------------------------------

# non-negative Least squares
# ADMM 
# min ||Xb-s||^2 + g_+(a) s.t. b == a
# 
def nnls(X,s):
    #print('NNLS')
    n,m = X.shape
    tol = 1e-7
    lam = 1
    XtXi = np.linalg.inv(np.dot(X.T,X) + (1/lam)*np.eye(m))
    Xts = np.dot(X.T,s)
    dif = 1
    a = np.zeros(m)
    b = np.random.randn(m)
    u = np.zeros(m)
    d = np.zeros(m)
    i = 0
    while dif > tol:
        a = np.dot(XtXi, Xts + (1/lam)*(b - u) )
        b = np.maximum( 0, a + u )
        d = a - b
        u += d
        dif = np.linalg.norm(d)/(np.linalg.norm(a) + 1e-8)
        #print('dif=',dif)
    return b

# ---------------------------------------------------------------------------------------

def least_sq(X,s):
    a,residuals,rank,sing = np.linalg.lstsq(X,s,rcond=None)
    return a

# ---------------------------------------------------------------------------------------

if __name__ == '__main__':
    #
    # ARGUMENTOS DE LINEA DE COMANDOS
    #
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--datadir", type=str, default="../data/calib",
                    help="path prefix  where to find files")
    ap.add_argument("-l", "--list", type=str, default="../data/calib/calib.list",
                    help="text file where input files are specified")
    ap.add_argument("-M", "--maxlen", type=int, default=16,
                    help="largo máximo de palabras a tener en cuenta en el score")
    ap.add_argument("-m", "--minlen", type=int, default=1,
                    help="largo mínimo de palabras a tener en cuenta en el score")
    #
    # INICIALIZACION
    #
    args = vars(ap.parse_args())
    print(args)
    datadir = args["datadir"]
    list_fname = args["list"]
    ocr_points = []
    true_points = []
    maxlen = args["maxlen"]
    minlen = args["minlen"]
    X = np.empty((0, maxlen - minlen + 2), float)  # vecores letra para cada archivo
    print(X.shape)
    s_lev = list() # np.empty((0, 2), float)  # lev and lsstr metrics
    s_man = list()
    s_col = list()
    #
    # abrimos lista de archivos
    # la lista es un archivo de texto con un nombre de archivo
    # en cada linea
    #
    with open(list_fname) as list_file:
        nimage = 0
        #
        # para cada elemento de la lista
        #
        manual = list()
        auto = list()

        por_categoria = list()
        for i in range(5):
            por_categoria.append(list())

        for relfname in list_file:
            #
            # proxima imagen
            #
            nimage = nimage + 1
            #
            # nombres de archivos y directorios de entrada y salida
            #
            relfname = relfname.rstrip('\n')
            reldir, fname = os.path.split(relfname)
            fbase, fext = os.path.splitext(fname)

            filedir = os.path.join(datadir, reldir)

            manual_fname = os.path.join(filedir, fbase + '.manual.txt')
            ocr_fname = os.path.join(filedir, fbase + '.ocr.txt')
            print(f'#{nimage} image={relfname} manual={manual_fname} ocr={ocr_fname}', end='')
            #
            # creamos carpetas de destino si no existen
            #
            ftxt = open(manual_fname, 'r')
            manual_text = ftxt.read()
            ftxt.close()
            ftxt = open(ocr_fname, 'r')
            ocr_text = ftxt.read()
            ftxt.close()
            manual_score = int(reldir[0])
            s_man.append(manual_score)
            s_col.append(cm.jet((5-manual_score)/4))
            #
            # ===========================================================
            #
            #
            # ocr_score = scores.score_dist_uno(ocr_text, 4)
            lev_fname = os.path.join(filedir, fbase + '.lev.txt')
            vec_fname = os.path.join(filedir, fbase + '.vec.txt')
            if False:
            #if os.path.exists(vec_fname):
                f = open(vec_fname,"r")
                vec = np.loadtxt(vec_fname)
            else:            
                vec_raw = scores.vec_score_raw(ocr_text, minlen, maxlen)
                vec = scores.vec_score(vec_raw)
                np.savetxt(vec_fname,vec)

            if os.path.exists(lev_fname):
                f = open(lev_fname,'r')
                lev = float(f.read())
                f.close()
            else:            
                lcs, lev = scores.tra_dist(ocr_text, manual_text)
                f = open(lev_fname,'w')
                f.write(str(lev))
                f.close()

            X = np.concatenate((X, [np.array(vec)]), axis=0)
            s_lev.append(lev)
            ocr_score = lev
            por_categoria[manual_score - 1].append(ocr_score)
            #
            # ===========================================================
            #
            print(f" manual={manual_score}  lev={ocr_score:6.4f}")
            manual.append(manual_score)
            auto.append(ocr_score)
            #
            # fin
            #

    max_r = 500  # cantidad de corridas de bootstrap
    numel = 40  # cantidad de muestras que me quedo por corrida
    s_lev = np.array(s_lev)
    #unos = np.ones((X.shape[0],1))
    #X = np.concatenate((X,unos),axis=1)
    #
    # minimos cuadrados comunes
    #
    w_ls = least_sq(X, s_lev)
    s_ls = np.dot(X, w_ls)

    w_boot = np.zeros( (max_r,len(w_ls)) )
    #
    # Lasso
    #
    model = lm.LassoCV(cv=5).fit(X,s_lev)
    w_lasso = model.coef_ 
    #s_lasso = np.dot(X,w_lasso)
    s_lasso = model.predict(X)
    
    plt.figure(figsize=(8,8))
    #
    # Bootstrap
    # 
    for r in range(max_r):
        indices = np.random.choice(X.shape[0], numel, replace=False).astype(int)
        Xr = X[indices]
        sr = s_lev[indices]
        wr = nnls(Xr,sr)
        w_boot[r,:] = wr
        s_r = np.dot(X, wr)

    w_b = np.mean(w_boot,axis=0)
    v_b = np.var(w_boot,axis=0)
    s_b = np.dot(X,w_b)

    print("Mínimos cuadrados con bootstrap\n", w_b)
    plt.plot([0,1],[0,1],'k--')
    #plt.scatter(s_lev,s_ls,color=s_col)
    plt.scatter(s_lev,s_b,color=s_col,marker='o')
    #plt.scatter(s_lev,s_lasso,marker='x',color=s_col)
    plt.axis((0,1,0,1))
    plt.grid(True)
    plt.xlabel('score ideal (Levenshtein)')
    plt.ylabel('score ajustado')
    plt.title('Relación entre score \'ideal\' basado en Levenshtein y score ajustado por LS')

    por_categoria = list()
    for i in range(5):
        por_categoria.append(list())
    for i in range(len(s_b)):        
        por_categoria[manual[i]-1].append(s_b[i])

    plt.figure(figsize=(8,8))
    plt.boxplot(por_categoria,notch=False)
    plt.grid(True)
    plt.xlabel('score manual (1 a 5)')
    plt.ylabel('score automatico (0 a 1)')
    plt.title('Score automático vs. score manual (palabras de 4 o más letras)')
    plt.show()
