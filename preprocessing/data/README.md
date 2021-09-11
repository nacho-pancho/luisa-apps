# Proyecto LUISA
## Archivos preprocesados

Este directorio contiene las versiones alineadas y recortadas según el algoritmo implementado en el [repositorio del proyecto](http://gitlab.fing.edu.uy/mh/imgproc.git/)

El directorio está organizado por rollos; cada carpeta se corresponde a un rollo.

Dentro de cada carpeta se encuentran las imágenes en formato TIF con compresión tipo FAX (CCITT GROUP 4).

Junto con cada imagen se encuentran otros tres archivos más, todos en texto plano. (La razón de por qué son archivos distintos es que cáda uno se genera en etapas distintas del procesamiento.)

* extensión **sha256**: hash SHA-256 de la imagen alineada en texto hexadecimal.
* extensión **meta**:   cuatro valores separados por comas: nombre base de la imagen, recorte horizontal, recorte vertical, ángulo de giro en grados (antihorario). Los recortes negativos indican __padding__, es decir, un en el recorte vertical -10 indica que se le agregan 10 lineas de pixeles arriba y abajo a la imagen. (Esto es para llevar todas las imágenes a el mismo tamaño y ahorrar tiempo de cómputo, ya que son cientos de miles.)
* extensión **blocks**: archivo CSV separado por espacios. Cáda linea contiene información acerca de un bloque segmentado en la imagen. Ese archivo se genera a partir de la matriz devuelta por la función `extract_blocks` del módulo C `microfilm.c` en el proyecto, que es donde se define el significado de cáda columna. Las columnas son:

..1 fila de la esquina superior izquierda del bloque en coordenadas de la imagen reducida (__no incluida en esta carpeta__)
..1 columna
..1 fila de la esquina inferior derecha
..1 columna 
..1 fila de la esquina superior izquierda del bloque en coordenadas de la imagen alineada (la correspondiente  con extensión **tif**)
..1 columna
..1 fila de la esquina inferior derecha
..1 columna
..1 número de fila de texto a la que pertenece el bloque (comienza en 0)
..1 número de bloque en la fila de texto a la que pertenece el bloque (comienza en 0)

De los anteriores, los primeros 4 no se utilizan en etapas ulteriores y pueden ignorarse. Los más importantes a los efectos de ubicar el bloque en la hoja son las columnas 5,6,7 y 8.

En general las coordenadas del bloque son bastante ajustadas al texto y pueden perderse detalles de las letras como ser vástagos de letras largas como 't','l','d', o las colas de letras como 'g','p', etc. Conviene entonces tomar un margen a cada lado del bloque recortado. Un valor que parece funcionar bien es de 8 pixeles.

## Índices de rollos y hojas

Además de lo archivos preprocesados se encuentran en la raíz de esta carpeta dos archivos de texto: `ROLLOS.txt` y `HOJAS.txt`. El segundo es simplemente una lista de las rutas relativas a este directorio de todas las hojas de todos los rollos. El primero es un CSV separado por comas en donde se encuentra información de cáda rollo. El archivo CSV en este caso contiene un cabezal que indica qué es cáda columna. A continuación se describe con más detalle dichos campos:

* **AÑO**: año en que fueron redactados lo documentos originales en papel.
* **NUMERO**: numero de rollo; éste es el indicador principal de un rollo a lo largo de todo el proyecto
* **ORIGEN**: departamento u organismo en donde se redactó el documento original (si se sabe)
* **NOMBRE_CORTO**: nombre corto del rollo. Este es el nombre con el que se encuentran en esta carpeta
* **NOMBRE_LARGO**: este es el nombre de las carpetas de los rollos tal cual nos fueron entregadas por la FIC.


