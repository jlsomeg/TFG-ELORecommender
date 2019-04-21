# TFG---RestFul-Web-App-Using-Python-Flask-and-MySQL-
------------------Use Instructions--------------------------
Tested on Windows 7
1. Go to the folder where it is located the .py file
2. Execute 'python mysql-test.py'
3. The python application will be launched in a port of your localhost http://127.0.0.1:5000/ for example
4. In a browser, enter the route 'http://127.0.0.1:5000/users/(user id you want to see)'



----------------------Conditions-----------------------------

1.May not work if you have different values in bbdd in this points

  a. connection = mysql.connector.connect(...) inside def __init__()
  
  b. sql_insert_query inside def insert_use()
  
2.Imports: Flask, render_template, request, pymysql, mysql.connector
3.Xampp up

----------------------Docker------------------------------------
1. Ten docker activo y corriendo
2. Solo hace falta que bajes de este repositorio el Dockerfile (o bajatelo entero como quieras) puesto que en 
el Dockerfile se encarga de clonar este repositorio a traves de github
3. En la carpeta donde tengas el repositorio ejecuta a traves de un terminal 'docker build -t nombrequequieras .'
4. A continuacion 'docker run -d -p 5000:5000 nombrequequieras'
5. Introduce 'docker-machine ip default' y te dara una ip
6. Probar si funciona con (la ip que te haya devuelto):5000/users/17
7. Se puede comprobar que ha ido mal consultando el id del contenedor con 'docker ps' y que te 
lo diga con 'docker logs (id)'

Para parar contenedores corriendo 'docker stop (id)'
