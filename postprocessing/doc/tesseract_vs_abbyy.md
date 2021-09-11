```
Javier Stabile
Federico Fioritto
Ernesto Fernandez
```
# Tesseract 4 VS Abbyy FineReader

# 14 VS Readiris 17

**Introducción 2
Evaluación 2
Resultados 3
Conclusiones 7**


```
Javier Stabile
Federico Fioritto
Ernesto Fernandez
```
## Introducción

En este documento se presentan y comparan los resultados obtenidos de tres aplicaciones
de OCR, Tesseract 4, Abbyy FineReader 14 y Readiris 17, para un conjunto de imágenes
escaneadas de microfilm de media y mala calidad, en particular documentos de la dictadura
Uruguaya.
Se decidió comparar estas tres aplicaciones por dos razones, una es las funcionalidades de
entrenamiento que brindan, y la otra es que se entendió que son las herramientas más
utilizadas para proyectos de la misma índole. Una limitante importante a la hora de decidir
qué aplicaciones evaluar fue que no se pudo utilizar una solución en la nube, debido a la
confidencialidad de los datos.

## Evaluación

Para evaluar cada una de las herramientas se tomó un conjunto reducido de imágenes de
prueba junto con sus transcripciones manuales y se comparó contra la salida brindada por
cada OCR, tomando en cuenta que cuanto más similar sea la salida a su respectiva
transcripción manual, mejor es el funcionamiento del OCR.
Ya que Abbyy fue el único OCR con cual se pudo entrenar y obtener resultados positivos,
se incluyeron distintas versiones del mismo las cuales se diferencian por la cantidad de
imágenes con las que se las entrenó. Es importante mencionar que el entrenamiento de
Abbyy consiste en generar una lista de imágenes de caracteres junto a su respectiva
transcripción la cual posee una cota superior de 1000 elementos, por lo que evidentemente
existe un límite en la capacidad de este proceso, al cual se llega relativamente rápido
(entrenando con 3 imágenes se definieron alrededor de 700 elementos). El entrenamiento
en Abbyy dió la idea de tener la finalidad de reconocer los caracteres usados
específicamente en la imagen con la que se entrenó, y no la de interpretarlos correctamente
en una nueva imagen.
Entrenar con caracteres muy deformados e ilegibles puede causar un reconocimiento de
peor calidad. Por ejemplo se tiene la siguiente palabra , por el contexto se
entiende que la segunda letra es una “e”, aunque visualmente sea similar a una “o”. Como
Abbyy utiliza un entrenamiento por caracter, especificando que el segundo caracter es una
“e” puede llegar a empeorar el reconocimiento correcto de otras “o” en el texto.
Por otro lado, como se mencionó en el documento sobre Tesseract, con el entrenamiento
no se logró resultados mejores en la salida del OCR, por lo que simplemente se utilizó
Tesseract con el lenguaje por defecto para español.


Javier Stabile
Federico Fioritto
Ernesto Fernandez
El entrenamiento con Readiris falló por mal funcionamiento del programa mismo, es decir
cada vez que se intentó entrenar el programa daba error. Por esta razón se experimentó
con el OCR sin entrenar.
Específicamente para medir resultados se utilizó la biblioteca difflib^1 de python, que provee
un conjunto de clases y funciones para la comparación de cadenas de caracteres. La clase

### utilizada fue ​ SequenceMatcher ​, y dentro de ella la función escogida fue ​ ratio ​, la cual retorna

una medida de la similitud entre dos textos representada como un número real en el rango
[0, 1]. Cuanto más cercano a uno, más similares son los textos comparados, mientras que
cuanto menor sea el valor indica que la diferencia es mayor.

## Resultados

En la ​ **tabla 1** se muestran los resultados obtenidos de comparar utilizando
_SequenceMatcher_ las salidas de cada OCR con su respectiva transcripción manual. Las

### imágenes ​ ent_1 ​, ​ ent_2 y ​ ent_3 son con las que se entrenó Abbyy. El modelo ​ Abbyy_1 se

### entrenó solo con ​ ent_1 ​, mientras que ​ Abbyy_1_2 fue con ​ ent_1 y ​ ent_2 ​, lo mismo para

### Abbyy_1_2_3 el cual utilizó ​ ent_1 ​, ​ ent_2 y ​ ent_3 ​. El grupo de imágenes que sigue en la

### tabla 1 (​ example_N ​) no fue utilizado para entrenar ningún modelo, sólo para medir

resultados.
**Tabla 1: Similitud entre salida del OCR y transcripción manual (de 0 a 1)
Imagen Abbyy Abbyy_1 Abbyy_1_2 Abbyy_1_2_3 Tesseract Readiris**
ent_1 0.8760 0.8768 **0.8775** 0.8722 0.6579 0.
ent_2 **0.7486** 0.6884 0.7114 0.6963 0.6502 0.
ent_3 0.0435 0.0648 0.0537 **0.2736** 0.1207 0.
example_1 **0.6686** 0.6529 0.6560 0.6614 0.6267 0.
example_2 **0.3893** 0.1274 0.2083 0.1243 0.1053 0.
example_3 0.0236 0.0542 0.0534 0.0647 **0.1947** 0.
example_4 0.3000 0.3245 **0.3667** 0.1816 0.2356 0.
example_5 0.7898 **0.8243** 0.7730 0.8206 0.5707 0.
example_6 0.1539 0.2706 **0.3061** 0.2961 0.0234 0.
example_7 0.4290 0.4121 **0.4510** 0.3278 0.3482 0.
example_8 0.2945 0.1396 **0.3737** 0.3377 0.2981 0.

(^1) ​https://docs.python.org/3/library/difflib.html#difflib.SequenceMatcher.ratio


Javier Stabile
Federico Fioritto
Ernesto Fernandez
Abbyy y sus distintas versiones de entrenamiento resultaron vencedores por sobre
Tesseract y Readiris. Este último tuvo una muy mala performance. La diferencia aquí vista
coincide con lo sensación que nos dio ver las salidas a simple vista. Además de los
resultados mostrados en la tabla, observamos que Abbyy, en comparación con Tesseract,
reconoce tanto las manchas de los bordes como una posible inclinación en la imagen y lo
corrige, por lo que esto genera usualmente una salida más similar al texto real ya que no
convierte como texto muchas de las manchas contenidas en la hoja.
En la ​ **gráfica 1** se muestra el promedio de cada OCR evaluado por sobre todos los
ejemplos vistos, donde se aprecia la tendencia de Abbyy sobre Tesseract, y bastante más
atrás está Readiris.
**Gráfica 1: Promedio similitudes OCRs (de 0 a 1)**
A continuación, en la ​ **imagen 1** ​se puede ver una porción de ejemplo de una de las

### imágenes usadas para entrenar, en particular la del entrenamiento 1 (​ ent_1) ​, la ​ imagen 2

muestra la salida producida por Abbyy sin entrenar, luego las imágenes ​ **imagen 3** ​, ​ **imagen
4** e ​ **imagen 5** son ​las salidas de Abbyy luego de entrenar con la ​ _ent_1, ent_1 y ent_2, y
ent_1, ent_2 y ent_3_ respectivamente. Más abajo la ​ **imagen 6** y la ​ **imagen 7** ​muestran las
salidas producidas por Tesseract y Readiris.


Javier Stabile
Federico Fioritto
Ernesto Fernandez
**Imagen 1: Porción original de la imagen** ​ **_ent__**
**Imagen 2: Salida de Abbyy
Imagen 3: Salida Abbyy_
Imagen 4: Salida Abbyy_1_**


Javier Stabile
Federico Fioritto
Ernesto Fernandez
**Imagen 5: Salida Abbyy_1_2_
Imagen 6: Salida Tesseract
Imagen 7: Salida Readiris**
La imagen utilizada anteriormente se considera de calidad media dado que contiene
caracteres que se pueden reconocer erróneamente pero son entendibles en su contexto.
Tras leer los resultados obtenidos, se aprecia que se corresponden los cálculos realizados
previamente ya que en promedio es Abbyy quien cometió la menor cantidad de errores.
La ​ _ent_3_ se considera de mala calidad dado que a simple vista no se logra entender todo el
texto y es difícil hacerlo incluso en su contexto. La ​ **imagen 8** muestra una porción de texto

### del ejemplo de entrenamiento 3 (​ ent_3 ​).


Javier Stabile
Federico Fioritto
Ernesto Fernandez
**Imagen 8: Porción original de la imagen** ​ **_ent__**
Tanto Readiris, Tesseract y Abbyy sin entrenar al procesar la ​ **imagen 8** ​, generaron como
salida alguna palabra legible y muchos caracteres sin sentido. Solo Abbyy_1_2_

### (entrenado con ​ ent_1 ​, ​ ent_2 y ​ ent_3) reconoció trigramas o frases correctamente aunque

también reconoció muchos caracteres sin sentido. Este comportamiento descrito se aprecia
en los resultados de los algoritmos en la ​ **tabla 1** ​, donde la similitud está en el orden del
segundo decimal excepto para Abbyy_1_2_3.

## Conclusiones

Luego de esta evaluación, se puede concluir que dado el tiempo restante del proyecto, el
tiempo invertido en estos experimentos y el objetivo del equipo, Abbyy resulta la mejor
opción para el primer paso de convertir las imágenes a texto, siendo superior en diez de los
once ejemplos vistos por un amplio margen sobre los demás OCRs.
Enfocándose ahora en las distintas versiones de Abbyy resultado del entrenamiento, es
difícil inferir a partir del reducido número de experimentos realizados (se lo puede llamar
reducido si se lo compara con la cantidad total de imágenes) si el hecho de agregar parejas
imagen/caracter a los modelos generará un cambio significativo a la hora de procesar el
resto de las imágenes, sin olvidar además que existe un límite de 1000 parejas para cada
modelo. La existencia de dicho límite acarrea el problema de decidir cuáles caracteres
integrarán el selecto grupo y cuáles no, teniendo como fuente miles y miles de documentos,
buscando siempre el objetivo de generar la salida óptima. El equipo cree que atacar de llano
el problema planteado anteriormente sería sumamente complejo y los experimentos para
decidir con criterio conllevarían una cantidad enorme de tiempo, es por esta razón que se
plantea la siguiente idea con el afán de reducir el dominio de posibilidades: entrenar con
documentos en buena calidad, para poder corregir caracteres visualmente similares a su
verdadero valor y que minimicen el ruido agregado al OCR. Evitando de esta forma asignar
a un símbolo valores deducidos por mero contexto que poco tengan que ver con la
representación fallida o poco legible del mismo. Una vez alcanzados los 1000 símbolos, no
continuar el proceso.



