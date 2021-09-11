# Diccionarios

Hay dos tipos de diccionarios en este repositorio:

+ Morfológicos.
+ Listas de palabras.

## Diccionarios Morfológicos

Sólo están los adecuados para **es_ANY**, o sea, cualquier español. Estos diccionarios son los que se usan para hacer stemming y tiene más información sobre  la morfología de la palabra. Estos archivos están en el directorio *spell* y por más datos se puede ver: [Man de Hunspell](https://www.systutorials.com/docs/linux/man/4-hunspell/)




## Apellidos

Los apellidos en los apellidos, tres archivos:

+ [apellidosFichas-limpios](./apellidos/apellidosFichas-limpios.txt): contiene un apellido por línea de los nombres de archivo de las fichas de desaparecidos. Las partes de los apellidos compuestos están en la misma línea (ej: da costa).
+ [apellidosLegajos-limpios](./apellidos/apellidosLegajos-limpios.txt): contiene los nombres tomados de las planillas de legajos.
+ [todosApellidos](./apellidos/todosApellidos.txt): contiene todos los anteriores con los agregados recuperados de Dbpedia.


* apellidos/apellidosFichas-limpios.txt
* apellidos/apellidosLegajos-limpios.txt
* apellidos/apellidos-fr.txt     Francés
* apellidos/apellidos-es-otr.txt Español (otros)
* apellidos/apellidos-es.txt     Español
* apellidos/apellidos-it.txt     Italiano
* apellidos/apellidos-ba.txt     Vascos
* apellidos/apellidos-en.txt     Inglés

## nombres

Los nombres están separados en [masculinos](./nombres/todosMasculinos.txt) y [femeninos](./nombres/todosFemeninos.txt).
Estos nombres fueron sacados de varias listas de nombres que hay en internet y de [Dbpedia](http://dbpedia.org) usando [sparql](http://dbpedia.org/sparql).

* nombres/todosFemeninos.txt
* nombres/todosNombres.txt
* nombres/todosMasculinos.txt

## Acrónimos

* acronimos/AcronimosEjercito.txt  Texto en prosa con descripción de los acrónimos
* acronimos/todosAcronimos.txt     Un acrónimo por linea
* acronimos/AcronimosFing.csv      Supongo que los mismos que en todosAcronimos pero con la descripción de qué es cada uno

## Palabras

Acá hay varias listas conseguidas de distintos lugares.

* palabras/linux_spanish.txt     Sacado de algún linux. No me acuerdo bien de dónde.
* palabras/diccionario.txt       Diccionario de palabras, no recuerdo de dónde salió.
* palabras/es0.txt               Tampoco recuerdo de dónde salió.
* palabras/lemario-20101017.txt  Tampoco recuerdo de dónde salió.
* palabras/badwords.txt          Lista de palabras transcritas por Tesseract pero no encontrada en uno de estos diccionarios (no recuerdo cuál)

### RAE

Cada linea tiene o bien una palabra suelta, o bien la palabra y su declinación femenina, ambas separadas por coma.

* palabras/rae.txt Todas las palabras juntas
* palabras/rae     Un archivo por inicial
