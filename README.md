# Explicaciones visuales para la gestión y la recomendación en jueces en línea

Trabajo Fin de Grado en Ingeniería Informática, Universidad Complutense de Madrid.

## Contenido

### Resumen

Este trabajo surge ante la necesidad de **introducir un sistema de recomendación de problemas para los usuarios de jueces en línea para facilitar la selección de problemas que los usuarios consideren relevantes o asequibles.** Esto servirá para amenizar la experiencia con los jueces en línea y disminuir la frustración de los usuarios a la hora de intentar resolver problemas que sobrepasan o subestiman su nivel de habilidad. Para ello hemos desarrollado **en python un sistema de recomendacion usando el metodo matematico ELO y desarrollando una aplicacion web que servira de campo de pruebas para estas recomendaciones**. El proyecto diferencia tres partes claras:

- Planteamiento de un sistema de puntuación para aproximar el nivel de habilidad de los usuarios y el nivel de dificultad de los problemas disponibles en un juez en línea.

- Diseño y desarrollo de un sistema de recomendación capaz de recomendar problemas a usuarios basándose en su habilidad y dificultad de los problemas.

- Diseño de un banco de pruebas en el que se pueda observar y gestionar de manera visual el comportamiento del sistema de puntuación y recomendación.

### Descripción del repositorio

El repositorio está dividido en tres partes que van de la mano con las partes establecidadas en el resumen:

1. **Memoria**
	
	Situado en la carpeta *TFGTeXiS-UTF8* en donde esta ubicado el pdf de la memoria que ha sido desarrollado usando LaTeX y todos los archivos necesarios para su construccion. En el archivo *TFGTeXiS.pdf* se habla en detalle de nuestro trabajo de fin de grado explicando cada paso, motivacion y especificaciones tecnicas del proyecto.
2. **Scripts de recomendación**

	Este conjunto actúa como el backend de la aplicación. En el se encuentran todos los scripts de python que conforman el sistema de recomendación. Son los encargados de cargar y procesar datos de la copia de la base de datos de ¡Acepta el reto! y realizar los cálculos y procesos para garantizar la construcción de un sistema de categorización ELO para usuarios y problemas. Contiene la lógica de las recomendaciones y el nivel de ELO y es el encargado de las modificaciones y consultas en la BD. Ejecuta las acciones requeridas del frontend. 
	
		Forman parte las carpetas *database* y *py_scripts* ademas de *forms.py*.
3. **Aplicacion Web**

	Este conjunto actúa como el frontend de la aplicación. Nuestro servicio ha sido implementado usando Flask3, un microframework para Python quepuede usarse para desarrollar aplicaciones web. La aplicación tiene varias rutas programadas a las que se puede acceder directamente a traves de la URL o a traves de hipervinculos en la aplicación y en donde estas ejecutanlos procesos que requiramos en los scripts de recomendacion. 
	
		Forman parte las carpetas *static* y *templates* ademas de *mysql-test.py*

### Despliegue

Ademas el repositorio ha sido encapsulado con la ayuda de Docker de manera que el despliegue, al ser totalmente automatizado, sea mucho más liviano, portable y sencillo, pudiéndolo probar en cualquier maquina que tenga instalado Docker sin el problema de añadir bibliotecas o dependencias con tan solo la ejecución de un comando.

	Forman parte los archivos *Dockerfile-app*,* Dockerfile-mysql*, *docker-compose.yaml* y *wait-for-it.sh*

Todas las instrucciones relacionadas con el despligue y lanzamiento de la aplicacion pueden encontrase en [Despliegue.MD](https://github.com/jlsomeg/TFG-ELORecommender/blob/master/Despliegue.MD)

## Autores

- Ederson Aldair Funes Castillo [@Kernel-13](https://github.com/Kernel-13)
- Jose Luis Gomez Alonso [@jlsomeg](https://github.com/jlsomeg)

## Directores

- Guillermo Jiménez Díaz [@gjimenezUCM](https://github.com/gjimenezUCM)
- Pedro Pablo Gómez Martín
