import psycopg2 as db
import socket
import hashlib
from io import BytesIO

DBHOST = '127.0.0.1'
DBPORT = 11543
DBUSER = 'captcha'
DBPASS = 'c4ptch4m4n'
DBNAME = 'lu_cons'

#
#=================================================
# interfaz simple sobre PostgreSQL
# (para no depender de ella)
#=================================================
#
#
# este módulo selecciona el host y puerto de conexión a la base de datos
# de manera distinta si se está dentro o fuera de FING
#
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect((DBHOST, 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP
#
# estamos en FING o no?
#
def within_fing():
    host_ip = get_ip().split('.')
    return host_ip[0] == '164' and host_ip[1] == '73'

if within_fing():
    #
    # en la red local FING
    #
    dbhost = 'yupanqui.fing.edu.uy'
    dbport = 5432
else:
    #
    # a través de tunel SSH
    # ssh -L 4444:yupanqui.fing.edu.uy:5432 ampere.fing.edu.uy
    #
    dbhost = 'localhost'
    dbport = 11543

dbconn = None
dbcursor = None

def connect():
    global dbconn,dbcursor
    if dbconn is None:
        dbconn = db.connect(host=DBHOST,
                            port=DBPORT,
                            user=DBUSER,
                            password=DBPASS,
                            database=DBNAME)
    return dbconn


def get_cursor():
    global dbcursor
    dbconn = connect()
    if dbcursor is None:
        dbcursor = dbconn.cursor()
    return dbcursor


def execute(sql,params=None):
    cursor = get_cursor()
    if params is None:
        cursor.execute(sql)
    else:
        cursor.execute(sql,params)


def fetch():
    cursor = get_cursor()
    return list( cursor.fetchall() )


def commit():
    conn = connect()
    conn.commit()


#
#=================================================
# interfaz de más alto nivel de acceso a los
# datos de la base
#=================================================
#
def get_rollos():
    execute("SELECT * FROM rollo ORDER BY numero")
    return fetch()


def get_num_rollo(nombre):
    execute(f"SELECT numero FROM rollo where nombre_corto='{nombre}'")
    return dbcursor.fetchone()


def get_hojas(rollo):
    if rollo is None:
        execute(f"SELECT * FROM hoja ORDER BY filename")
    else:
        execute(f"SELECT * FROM hoja WHERE rollo={rollo} ORDER BY filename")        
    return fetch()

def get_texto(hb):
    execute(f"SELECT * FROM texto WHERE hashidbloque='{hb}'")
    return fetch()

    
def get_bloques(hh):
    execute(f"SELECT * FROM bloque WHERE hashhoja='{hh}' ORDER BY indice")
    return fetch()


def get_block_hash(b):
    return hashlib.sha256("{0:s}-{1:d}-{2:d}-{3:d}-{4:d}".format(b[1], b[6], b[7], b[8], b[9]).encode(encoding='utf-8')).hexdigest()


def insert_block(brow,bimage):
    with BytesIO() as image_blob: # save image as TIFF file to memory bffer image_blob
        bimage.save(image_blob,format="tiff",compression="group4")
        bimage_blob_hex = image_blob.getvalue().hex()
    hash = get_block_hash(brow)
    query = f"insert into bloque (rollo,hoja,stop,sleft,sbottom,sright,ltop,lleft,lbottom,lright,row,col,hash,tiffdata) \
            values ({brow[0]},'{brow[1]}',{brow[2]},{brow[3]},{brow[4]},{brow[5]},{brow[6]},{brow[7]},{brow[8]},{brow[9]},{brow[10]},{brow[11]},'{hash}','{bimage_blob_hex}')"
    #print(query)
    execute(query)


def update_block(hash,text,image):
    with BytesIO() as image_blob: # save image as TIFF file to memory bffer image_blob
        image.save(image_blob,format="tiff",compression="group4")
        image_blob_hex = image_blob.getvalue().hex()
        queryformat = "UPDATE bloque SET text=%s,tiffdata=%s WHERE hash=%s"
        execute(queryformat,(text,image_blob_hex,hash))


def update_hoja_score(nombre,score):
        execute(f"UPDATE hoja SET score={score} WHERE nombre='{nombre}'")


def update_block_score(hash,score):
        execute(f"UPDATE bloque SET score={score} WHERE hash='{hash}'")


def get_hojas_buenas(rollo,umbral):
    if umbral is None:
        umbral = 0.7
    if rollo is None:
        execute(f"SELECT * FROM hoja WHERE score > {umbral} ORDER BY nombre")        
    elif len(rollo) == 0:
        execute(f"SELECT * FROM hojas WHERE score > {umbral} ORDER BY nombre")        
    else:
        execute(f"SELECT * FROM hojas WHERE rollo={rollo} AND score > {umbral} ORDER BY nombre")
    return fetch()

    
def get_bloques_buenos(hoja,minscore=1.0,minlength=2):
    symbols = '.!$%&,()*+,-./:;<=>?@{{}}[]\\x2c\\x22#'
    query = f"SELECT * FROM bloque WHERE hoja='{hoja}' AND score >= {minscore} AND LENGTH(TRIM('{symbols}' FROM text)) >= {minlength} ORDER BY row,col"
    execute(query)
    return fetch()
        
