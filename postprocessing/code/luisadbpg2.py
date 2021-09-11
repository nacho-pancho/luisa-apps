# -*- coding: utf-8 -*-
#
# interfaz con base de datos
# version emprolijada y mejorada 
#
import psycopg2 as dbserver
import time
import config

#Port=11543 ### Puerto para la conexión a la base del servidor de desarrollo
#
# estado global del módulo
Debug=False
Trace=False

#----------------------------------------------------------------------------

dbconn = None
dbcursor = None

def getConnection(host=config.DB_HOST, 
                  port=config.DB_PORT, 
                  user=config.DB_USER,
                  password=config.DB_PASS, 
                  dbname=config.DB_NAME):
    '''
    Devuelve la instancia única de la base de datos utilizada en todas las transacciones.
    Si no existe se crea la instancia por única vez; de ahí en más se devuelve su referencia
    '''
    global dbconn
    if dbconn is None:
        dbconn = dbserver.connect(host=host,port=port,user=user,password=password,dbname=dbname)
    return dbconn
        
#----------------------------------------------------------------------------
         
def getCursor():
    '''
    Devuelve el cursor por defecto utilizado en todas las transacciones.
    Si no existe se crea por única vez; de ahí en más devuelve su referencia
        
    '''
    global dbcursor
    if dbcursor is None:
        conn = getConnection()
        dbcursor = dbconn.cursor()
    return dbcursor

#----------------------------------------------------------------------------
    
def queryExec(query,params=None):
    '''
    ejecuta un query en la DB
    '''
    cursor = getCursor()        
    if Debug:
        print('DEBUG:',query," params:",params)
    try:
        cursor.execute(query,params)
    except dbserver.Error as e:
        print(e.pgerror)
        raise e
    return cursor


#----------------------------------------------------------------------------

def callProc(proc,params=[]):
    '''
    ejecuta un stored procedure en la DB
    '''
    tic = time.time()
    cursor = getCursor()
    res=dbcursor.callproc(proc,params)
    print("TRACE: callProc ",proc, time.time()-tic,"s.")
    return cursor

#----------------------------------------------------------------------------

def commit():
    tic = time.time()
    conn = getConnection()
    conn.commit()
    if Trace:
        print("TRACE: commit:",time.time()-tic,"s.")

