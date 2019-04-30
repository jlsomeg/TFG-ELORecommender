from flask import Flask, render_template, request
import pymysql
from py_scripts import ACR_Plots as pl

app = Flask(__name__)

class Database:
	def __init__(self):
		self.conn = pymysql.connect(host='acr-mysql',
									database='acr_dat',
									user='dev',
									password='dev')

		self.cursor = self.conn.cursor()

	def insert_user(self, userId, users_elo):
		sql_insert_query = "INSERT INTO User_Scores (user_id, elo_global) VALUES (%s, %s)"
		insert_tuple = (userId, users_elo)
		self.cursor.execute(sql_insert_query,insert_tuple)
		self.conn.commit()
		print("Record inserted successfully into python_users table")

	def user_submissions(self,userId):
		sql_insert_query = "SELECT id, problem_id, status, submissionDate FROM submission WHERE user_id=%d ORDER BY submissionDate DESC" % (int(userId))
		self.cursor.execute(sql_insert_query)
		return self.cursor.fetchall()

	def problem_list(self):
		self.cursor.execute("SELECT internalId, title, totalDistinctUsers FROM problem ORDER BY internalId ASC")
		return self.cursor.fetchall()

	def user_list(self):
		self.cursor.execute("""SELECT user_id, COUNT(DISTINCT(problem_id)), SUM(CASE 
								WHEN status = 'AC' THEN 1 
								WHEN status = 'PE' THEN 1 
								ELSE 0 END) FROM submission 
								GROUP BY user_id 
								ORDER BY user_id ASC""")
		return self.cursor.fetchall()

	def close_conn(self):
		self.conn.close()

### User / Problem / General Dash

@app.route('/users/<user_id>')
def dash_user(user_id):
	db = Database()
	user_info = db.user_submissions(user_id)	# List of the user's latest submissions
	div_plot_user_evolution = pl.GRAPH_USERS_EVOLUTION(db.cursor, user_id)		# User ELO evolution plot (in HTML code)
	div_plot_user_progress = pl.GRAPH_USER_PROBLEM_PROGRESS(db.cursor, user_id) # user problem completion pie chart (in HTML code)
	div_plot_user_categories = pl.GRAPH_USER_CATEGORIES(db.cursor, user_id) 	# User ELOs per category (in HTML code)
	db.close_conn()

	return render_template('user_dash.html', evolution=div_plot_user_evolution, progress=div_plot_user_progress, 
		categories=div_plot_user_categories, user_id=user_id)
	#return render_template('user_dash.html')

@app.route('/problems/<problem_id>')
def dash_problems(problem_id):
	db = Database()
	div_plot_problem_evolution = pl.GRAPH_PROBLEMS_EVOLUTION(db.cursor, problem_id)	# Problem ELO evolution plot (in HTML code)
	div_plot_user_progress = pl.GRAPH_PROBLEM_SOLVE_RATIO(db.cursor,problem_id)  # problem completion pie chart (in HTML code)
	db.close_conn()
	return render_template('problem_dash.html', evolution = div_plot_problem_evolution,progress=div_plot_user_progress, problem_id=problem_id)
	#return render_template('index.html', result=res, content_type='application/json')

@app.route('/stats')
def dash_general():
	db = Database()
	div_hist_users_elo_distribution = pl.GRAPH_ELO_DISTRIBUTION(db.cursor, 'Users')			# Users ELO distribution histogram (in HTML code)
	div_hist_problems_elo_distribution = pl.GRAPH_ELO_DISTRIBUTION(db.cursor, 'Problems')	# Problems ELO distribution histogram (in HTML code)
	div_bars_tries_till_solved = pl.GRAPH_TRIES_AVERAGE(db.cursor)
	db.close_conn()

	#return render_template('stats.html', users_hist=div_hist_users_elo_distribution, problems_hist=div_hist_problems_elo_distribution)

@app.route('/problems')
def list_problems():
	db = Database()
	problems = db.problem_list()
	db.close_conn()
	return render_template('problems.html', problems=problems)

@app.route('/users')
def list_users():
	db = Database()
	users = db.user_list()
	db.close_conn()
	return render_template('users.html', users=users)

### Unknown

@app.route('/signup')
def signup():
	return render_template('signup.html')

@app.route('/forms')
def forms():
	return render_template('forms.html')

@app.route('/bootstrap-elements')
def bootstrapelements():
	return render_template('bootstrap-elements.html')

### Insert User

@app.route('/insert_user')
def insert_user():
	return render_template('insert-user.html')

@app.route('/new_user',methods=['POST'])
def usuario():

	userid = request.form['user_id']
	userELO = request.form['users_elo']
	if userELO =="":
		userELO = 8.0

	db = Database()
	db.insert_user(userid,userELO)
	db.close_conn()

	return render_template('insert-user-sucess.html', data =userid )

if __name__ == '__main__':
	app.run(port=8181, host="0.0.0.0")

