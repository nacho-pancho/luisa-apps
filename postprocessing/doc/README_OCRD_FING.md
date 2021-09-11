```
Javier Stabile
Federico Fioritto
Ernesto Fernandez
```
# Entrenando Tesseract para

# reconocimiento de imágenes de

# mala calidad.

## Introducción

El documento presenta los conocimientos y resultados obtenidos en base a la investigación
realizada para entrenar Tesseract, para un conjunto de imágenes escaneadas de microfilm
y con mala calidad, en particular documentos de la dictadura Uruguaya.
El objetivo del documento es que sirva de guía para quien quiera entrenar Tesseract y no
encuentra documentación adecuada.
Cabe destacar que logramos entrenar la red neuronal, pero no obtuvimos una mejor salida
que la obtenida por los lenguajes ya entrenados por defecto^1.

## Aplicaciones utilizadas

```
● Tesseract versión 4
● Ubuntu 16.04: Fue con el único que pudimos hacerlo funcionar luego de probar con
ubuntu 14.04 y Windows 10
● OCR-D Train^2 : Proyecto creado para facilitar el entrenamiento de Tesseract 4
mediante un makefile que busca e instala todas las dependencias
● ImageMagick^3
● LUISA^4 : plataforma colaborativa creada por la FING para transcribir bloques de texto
```
## Preparando ambiente:

En Ubuntu 16.04 (Recomendado: instalación limpia)

1. Clonar repositorio OCR-D Train:
git clone https://github.com/OCR-D/ocrd-train.git
2. Pararse en la carpeta del proyecto e instalar Leptonica y tesseract:
cd ocrd-train
make leptonica tesseract

(^1) ​https://github.com/tesseract-ocr/tessdata_best
(^2) ​https://github.com/OCR-D/ocrd-train
(^3) ​https://imagemagick.org
(^4) ​https://www.fing.edu.uy/mh/luisa/docdic


Javier Stabile
Federico Fioritto
Ernesto Fernandez
Luego de esto tendrán instalado leptonica y tesseract localmente en el repositorio ocrd-train.
Las versiones instaladas son las que están por defecto, pero se puede actualizar fácilmente
modificando el archivo ​Makefile​.

## Directorios y archivos

El script principal que contiene los comandos para ejecutar el entrenamiento es ​Makefile​.
El resto de archivos a tener en cuenta se encuentran la carpeta ​ **data** ​. Los mismos son:
● **ground-truth:** En esta carpeta van los bloques de imágenes en formato ​.tif y su
respectiva transcripción en formato ​.gt.txt​. Luego de entrenar se van a generar los
.box​ y ​.lstmf​ correspondientes.
● **all-boxes:** Lista la ubicación de todos los archivos ​.box​, separando cada uno por
medio de un salto de línea.
● **all-lstmf:** Lista de ubicaciones de todos los archivos ​.lstmf​. El número de líneas
del archivo es la cantidad total de archivos de entrenamiento.
● **list.eval:** ​ Lista de ubicaciones de todos los archivos utilizados para evaluar.
● **list.train:** ​ Lista de ubicaciones de todos los archivos utilizados para entrenar.
● **radical-stroke.txt y unicharset:** ​ Archivos utilizados para el entrenamiento.
Los únicos archivos que es necesario agregar manualmente son los ​.tif y ​.gt.txt en la
carpeta ground-truth. Los restantes se generan automáticamente al ejecutar el proceso de
entrenamiento. Los archivos ​.tif son las imagenes que se utilizarán para el
entrenamiento, mientras que los ​.gt.txt son archivos de texto conteniendo las
traducciones de los ​.tif asociados. Dicha asociación se dá a través de los nombres de los
archivos, por ejemplo, la imagen ​bloque1.tif se corresponde con el archivo de texto
bloque1.gt.txt​.

## Entrenamiento

Luego de tener el ambiente preparado y los archivos con extensión ​.tif y ​.gt.txt en el
directorio ground-truth. Ubicados en la raíz del proyecto basta con ejecutar:
make training
Esta regla ejecutará distintos comandos para generar los archivos necesarios para el
entrenamiento, brindando detalles de las distintas iteraciones del entrenamiento en la
terminal.
Una vez terminado el proceso, en la carpeta ​ **_data_** ​se genera un archivo con el
entrenamiento obtenido (por defecto ​foo.traineddata​), el cual puede ser utilizado para
transcribir una imagen moviendolo a la carpeta ​ **_tessdata_** del Tesseract instalado en el
sistema en cuestión, e indicando a Tesseract que se quiere utilizar ese lenguaje mediante la
flag brindada (-l en Tesseract 4).


```
Javier Stabile
Federico Fioritto
Ernesto Fernandez
```
## Detalles

```
● En el archivo ​Makefile del proyecto OCR-D Train se pueden modificar bastantes
variables, una importante es el lenguaje que usa como punto de inicio del
entrenamiento, que por defecto es el inglés.
● Se puede utilizar tanto Tesseract que se instala dentro del proyecto OCR-D Train,
como cualquier otro instalado en el sistema o incluso en otro equipo, el archivo
.traineddata es el que contiene todo lo referido al entrenamiento y se puede usar
en cualquier Tesseract (por lo menos de la versión 4)
```
## Preprocesamiento

Antes de entrar en el detalle de las pruebas y resultados obtenidos, es interesante resumir
los distintos pre procesamientos realizados sobre los datos disponibles:
● Agregar márgenes a los bloques: En base a lo leído en la web y documentación de
Tesseract, y además luego comprobarlo, es importante que los bloques utilizados
para entrenar tengan un margen blanco antes de llegar al borde de la imagen, en
base a nuestra experiencia, dejando 30 pixeles de margen fue suficiente. Esto se
puede hacer fácilmente con ImageMagick.
● Descartar bloques que contengan el caracter “@”: En base a las instrucciones de
LUISA, los bloques que contengan este caracter son bloques ilegibles (por un
humano) por lo que no aportan al entrenamiento.
● Descartar bloques que sean manchas: Siguiendo las instrucciones de LUISA, estos
bloques son los que no tienen transcripción (string vacío).
● Descartar bloques con menos de 90% de acierto entre las transcripciones: Dado que
algunos bloques pueden ser confusos incluso para el ojo humano, consideramos
que las transcripciones que no coincidan en un 90% tienen gran probabilidad de ser
erróneas.
● Descartar bloques con menos de 3 transcripciones de distintos usuarios: Sumado al
punto anterior, buscamos asegurarnos que la transcripción sea siempre la correcta,
algunos bloques cumplían con el 90% de acierto, por tener una única transcripción.
● Descartar bloques cuya transcripción no tenga ningún caracter alfanuméricos.
● Descartar bloques con transcripciones de menos de 3 letras.


```
Javier Stabile
Federico Fioritto
Ernesto Fernandez
```
## Resultados y Conclusiones

Es importante mencionar que la principal dificultad que se encontró al intentar entrenar
Tesseract fue la calidad de la documentación existente sobre la herramienta y en específico
sobre su entrenamiento. La wiki del proyecto oficial en github^5 no es clara, no está completa,
y muchas veces es errónea. La principal fuente para buscar información y resolver dudas
fue un foro público de google al cual se hace referencia desde la wiki como sitio de
preguntas^6. Fue allí dónde dimos con usuarios que recomendaban la utilización del proyecto
OCR-D Train como alternativa a entrenar siguiendo la wiki, la cual dicho ya de paso
catalogan como confusa e incompleta.
Bajo este contexto es que se comenzó con la tarea de intentar mejorar la salida de tesseract
sobre los documentos históricos.
El primer reto autoimpuesto fue simple, entrenar con un pequeño recuadro en el que se leía
sólo la palabra “detenido” y para el cual el ​spa.traineddata ​devolvía “deteter”. Tras largas
horas de prueba y error configurando el proyecto, finalmente se logró construir un archivo
.traineddata el cual generaba la salida correcta para el bloque mencionado. Por lo que
aunque la prueba fue bastante naive, y se evaluó con el mismo conjunto que se entrenó, los
resultados fueron alentadores para el grupo ya que había un progreso.
A partir de este punto se pasó a entrenar con datos provistos por la plataforma LUISA.
Básicamente se contó por un lado con un gran número de imágenes en formato .tif
(llamadas bloques) las cuales eran recortes de los documentos históricos e idealmente
contenían una única palabra (a veces señalaban manchas, signos de puntuación, líneas,
etc). Por otro lado se tenía un número variable de inputs de usuarios para cada bloque
indicando su contenido.
Se probó distintas estrategias de preprocesamiento de los datos. En principio se descartó
todo bloque no identificado como palabra por los usuarios y todo bloque no legible
(transcripción vacía y transcritos como “@” respectivamente, siguiendo las instrucciones de
la plataforma LUISA). Además, definimos la transcripción de cada bloque, como la
transcripción más común del conjunto dado. Tras entrenar con un 80% del subconjunto
obtenido los resultados fueron desalentadores: no sólo habían empeorado con respecto al
tesseract por defecto, sino que no tenían sentido alguno, para un documento con palabras
legibles devolvía prácticamente sólo puntos y guiones como salida.
Con esto en mente, tras investigar el conjunto de datos de entrenamiento, encontramos que
un gran número de bloques y transcripciones contenían en su mayoría puntos y guiones.
Decidimos entonces considerar como transcripciones “válidas” aquellas que contengan por
lo menos un caracter alfanumérico y el largo de la palabra sea de por lo menos 3 letras. Los
resultados aquí variaron levemente, el texto de salida siguió sin tener sentido pero se

(^5) ​https://github.com/tesseract-ocr/tesseract/wiki/TrainingTesseract-4.
(^6) ​https://groups.google.com/forum/#!forum/tesseract-ocr


Javier Stabile
Federico Fioritto
Ernesto Fernandez
podían apreciar otros símbolos y letras además de puntos y guiones como en el caso
anterior.
Para una siguiente prueba, además de las restricciones mencionadas anteriormente, se
tomó en cuenta sólo los bloques tales que las transcripciones más comunes abarquen un
90% del total para esos bloques, y que además tuvieran un mínimo de 3 transcripciones
válidas. Los resultados siguieron siendo igual de malos, siempre comparando con el
entrenamiento brindado en Tesseract por defecto.
Dado que los resultados fueron obtenidos utilizando grandes cantidades de datos y sin
mucha validación previa a nivel de imagen, probamos también entrenando con un conjunto
de datos más chico y de mejor calidad de imagen reconocido por nosotros, con el fin de
probar si los ejemplos de entrenamiento podrían estar empeorando más al entrenamiento
debido a la claridad de los bloques. Por no conocer una manera automática de detectar
cuándo y cuánto un bloque es más legible que otro, este conjunto terminó siendo bastante
chico y también terminó mostrando peores resultados que la red entrenada por defecto para
el español que brinda Tesseract.
Luego de fallar en el intento de llegar a resultados utilizables en una etapa temprana del
proyecto, se decidió a desistir a esta tarea para comenzar a trabajar con lo que es el
procesamiento del lenguaje natural sobre las salidas. Si bien el grupo tuvo grandes
esperanzas en poder hacer un buen uso de los datos aportados por LUISA, el
entendimiento a fondo de la ingeniería de Tesseract para hacer un entrenamiento efectivo
escapa al alcance de este proyecto de grado. No obstante, seguimos investigando
herramientas OCR que nos puedan ser más útiles que Tesseract sin entrenamiento, aunque
sabiendo que no podrán ser utilizados los datos aportados por LUISA (o al menos no
fácilmente) para entrenar, y tenemos esperanza de que la aplicación Abbyy FineReader 14
nos sea de utilidad.
Esperamos que este documento sea de utilidad como puntapié inicial para futuros trabajos
sobre Tesseract.



