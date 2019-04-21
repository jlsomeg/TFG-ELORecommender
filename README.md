# TFG---RestFul-Web-App-Using-Python-Flask-and-MySQL-
------------------Use Instructions--------------------------
Tested on Windows 7
1. Go to the folder where it is located the .py file
2. Execute 'python mysql-test.py'
3. The python application will be launched in a port of your localhost http://127.0.0.1:5000/
4. In a browser, enter the route 'http://127.0.0.1:5000/users/(user id you want to see)'

----------------------Conditions-----------------------------

1.May not work if you have different values in bbdd in this points

  a. connection = mysql.connector.connect(...) inside def __init__()
  
  b. sql_insert_query inside def insert_use()
  
2.Imports: Flask, render_template, request, pymysql, mysql.connector
3.Xampp up
