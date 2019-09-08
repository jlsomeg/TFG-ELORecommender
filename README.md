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

----------------------Docker------------------------------------
1. Ten Docker(con Docker-Compose) corriendo / Have docker(with Docker-Compose) running

2. Descarga los archivos del repositorio / Download the repository files

	2a. Si lo haces con git clone en Windows, ejecuta antes 'git config --global core.autocrlf false' para que este no convierta finales de línea al estilo Windows \r \n en lugar de los finales de línea \n que bash espera.
    
3. En la carpeta donde tengas el repositorio ejecuta a traves de un terminal 'docker-compose up' / In the folder where you have the repository run through a terminal 'docker-compose up'

    3a. En caso de querer eliminar los contenedores usa 'docker-compose down --rmi all' / 
If you want to eliminate the containers use 'docker-compose down --rmi all'

4. Las imagenes se crearan a partir de las instrucciones introducidas en los Dockerfiles y en el yalm Docker-Compose / The images will be created from the instructions entered in the Dockerfiles and in the yalm Docker-Compose

    4a. El sofwtare crea 2 imagenes, - acr-mysql donde se alojara la bd y - acr-app donde se alojara el servicio web
    
    4b. Las imagenes correran sobre la ultima distribucion de ubuntu usando python3, entre otras dependencias / The images will run on       the last distribution of ubuntu using python3, among other dependencies
    
    4c. Se prodra acceder a la db a traves del puerto 3306 y al servicio web a traves del puerto 8181 / The db can be accessed through       port 3306 and the web service through port 8181
    
    4d. Para la sincronizacion entre contenedores, se ha utilizado la herramienta wait-for-it //  For the synchronization between containers, the wait-for-it tool has been used
    
5. El script de docker-compose lanzara los contenedores en sus respectivos puerto de manera sincronizada y se encargara de la comunicacion entre estos / The docker-compose script will launch the containers in their respective ports in a synchronized manner and will take care of the communication between them

6. Podremos probar si el servicio funciona en rutas como por ejemplo http://192.168.99.100:8181/problem_list / We can test if the service works on routes such as http://192.168.99.100:8181/problem_list

Usar 'docker system prune -a' para limpiar de vez en cuando / Use 'docker system prune -a' to clean once in a while
----------------------Conditions without docker-----------------------------
1. Cambiar los valores pymysql.connect por los de tu base de datos en localhost / Change the values pymysql.connect to those of your database in localhost

2. En mysql_test.py, cambiar app.run() por el host y el puerto donde vas a colgar el servicio / In mysql_test.py, change app.run () to the host and port where you are going to hang the service

3.Import: Flask, flask_restful, request, pymysql, mysql.connector,flask_wtf,wtforms,plotly

4.Xampp up (mysql and apache)

