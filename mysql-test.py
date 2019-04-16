from flask import Flask, render_template, request
import pymysql, mysql.connector

app = Flask(__name__)

class Database:
    def __init__(self):
        try:
            connection = mysql.connector.connect(host='127.0.0.1',
                                         database='tfg',
                                         user='root',
                                         password='')
            self.con = connection
        except mysql.connector.Error as error:
            connection.rollback()  # rollback if any exception occured
            print("Failed connection into python_users table {}".format(error))

    def insert_use(self,userId,users_elo):
        cursor = self.con.cursor()
        sql_insert_query = """ INSERT INTO `users_elo` (`user_id`, `users_elo`) VALUES (%s, %s)"""
        insert_tuple = (userId, users_elo)
        cursor.execute(sql_insert_query,insert_tuple)
        self.con.commit()
        print("Record inserted successfully into python_users table")

    def user_problems(self,userId):
        cursor = self.con.cursor()
        sql_insert_query = """ SELECT * FROM `submission` WHERE `user_id`= 11611 ORDER BY `submissionDate` DESC"""
        insert_tuple = (userId)

        cursor.execute(sql_insert_query)
        result = cursor.fetchall()
        return result



@app.route('/users/<user_id>')
def dash_user(user_id):

    def db_query():
        db = Database()
        problems = db.user_problems(user_id)

        return problems

    usuario = db_query()



    return render_template('index.html', usuario=usuario, content_type='application/json')

@app.route('/probelms/<user_id>')
def dash_problems(user_id):
    data = user_id
    return render_template('index.html', data=data)
    #return render_template('index.html', result=res, content_type='application/json')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')
@app.route('/blog')
def blog():
    return render_template('blog.html')
@app.route('/signup')
def signup():
    return render_template('signup.html')
@app.route('/register')
def register():
    return render_template('register.html')
@app.route('/timeline')
def timeline():
    return render_template('timeline.html')
@app.route('/forms')
def forms():
    return render_template('forms.html')
@app.route('/typography')
def typography():
    return render_template('typography.html')
@app.route('/bootstrap-elements')
def bootstrapelements():
    return render_template('bootstrap-elements.html')
@app.route('/insert_user')
def insert_user():
    return render_template('insert-user.html')

@app.route('/new_user',methods=['POST'])
def usuario():

 userid = request.form['user_id']
 userELO = request.form['users_elo']
 if userELO =="":
     userELO = 8.0

 def db_query():
     db = Database()
     db.insert_use(userid,userELO)

 db_query()

 return render_template('insert-user-sucess.html', data =userid )



