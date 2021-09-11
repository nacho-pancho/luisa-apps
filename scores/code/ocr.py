import subprocess

TESS_DATA      = "/home/DOCDIC/tesseract/software/TESSDATA_AG/tessdata_fast"
TESS_CONFIG    = f'-l spa --tessdata-dir {TESS_DATA}' 

#------------------------------------------------------------------------------

def execute_tesseract(img_filename, output_noext):
    if img_filename[-3:] == 'tif':
        tmpname = img_filename[:-3]
        command = f'convert -format png "{img_filename}" /tmp/tess.png'
        subprocess.call(command, shell=True)
        img_filename = '/tmp/tess.png'
    command = f'tesseract {TESS_CONFIG} "{img_filename}" "{output_noext}"'
    subprocess.call(command, shell=True)

def execute_abbyy(img_filename,output_noext):
    '''
    
    ABBYY es un OCR comercial.
    
    Yo conseguí una versión de prueba del SDK, y compilé el código de ejemplo "CommandLineInterface".
    El ejecutable (de nombre CommandLineInterface) lo puse como link simbólico en /usr/local/bin/abbyy
    
    Para correr el programa tuve que agregar las librerias de ABBYY a la ruta del linker dinámico.
    
    Para eso creé un archivo /etc/ld.so.conf.d/abbyy.conf con el siguiente contenido:
    
    /opt/ABBYY/Bin
    
    La carpeta /opt/ABBYY es la ruta en donde instalé el SDK. Luego actualicé la base de datos del linker
    con 

    sudo ldconfig
    
    y con eso alcanzó.

    '''
    #abbyy -rl Spanish -if /workspace/luisa/calidades/5/r1060-011.png -f TextUnicodeDefaults -of /tmp/pepe.txtv
    command = f'abbyy -rl Spanish -if "{img_filename}" -f TextUnicodeDefaults -of "{output_noext}.txt"'
    subprocess.call(command, shell=True)
