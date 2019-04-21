from flask import Flask, render_template, request
import pymysql

app = Flask(__name__)

class Database:
    def __init__(self):
        try:
            connection = pymysql.connect(host='localhost',
                                         database='tfg',
                                         user='root',
                                         password='')
            self.con = connection
        except pymysql.Error as error:
            self.con.rollback()  # rollback if any exception occured
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
        sql_insert_query = """ SELECT `id`,`problem_id`,`status`, `submissionDate`  FROM `submission` 
        WHERE `user_id`= '%s' ORDER BY `submissionDate` DESC""" % (userId)

        cursor.execute(sql_insert_query)
        result = cursor.fetchall()
        return result



@app.route('/users/<user_id>')
def dash_user(user_id):

    def db_query():
        db = Database()
        problems = db.user_problems(user_id)

        return problems

    usuario_info = db_query()



    return render_template('index.html', usuario_info=usuario_info,user_id=user_id, content_type='application/json')

@app.route('/probelms/<user_id>')
def dash_problems(user_id):
    data = user_id
    return render_template('index.html', data=data)
    #return render_template('index.html', result=res, content_type='application/json')


@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/forms')
def forms():
    return render_template('forms.html')

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

if __name__ == '__main__':
    app.run(host='0.0.0.0')

