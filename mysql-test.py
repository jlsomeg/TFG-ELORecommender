from flask import Flask, render_template, request
from py_scripts import ACR_Plots as pl
from py_scripts import DB_Functions as db

app = Flask(__name__)

### Dashes

@app.route('/users/<user_id>')
def dash_user(user_id):
	user_info = db.user_submissions(user_id)									# List of the user's latest submissions
	div_plot_user_evolution = pl.GRAPH_USERS_EVOLUTION(db.__cursor, user_id)		# User ELO evolution plot (in HTML code)
	div_plot_user_progress = pl.GRAPH_USER_PROBLEM_PROGRESS(db.__cursor, user_id) # user problem completion pie chart (in HTML code)
	div_plot_user_categories = pl.GRAPH_USER_CATEGORIES(db.__cursor, user_id) 	# User ELOs per category (in HTML code)

	return render_template('user_dash.html', evolution=div_plot_user_evolution, progress=div_plot_user_progress, 
		categories=div_plot_user_categories, user_id=user_id)

@app.route('/problems/<problem_id>')
def dash_problems(problem_id):
	div_plot_problem_evolution = pl.GRAPH_PROBLEMS_EVOLUTION(db.__cursor, problem_id)	# Problem ELO evolution plot (in HTML code)
	div_plot_user_progress = pl.GRAPH_PROBLEM_SOLVE_RATIO(db.__cursor,problem_id)  		# problem completion pie chart (in HTML code)
	return render_template('problem_dash.html', evolution = div_plot_problem_evolution,progress=div_plot_user_progress, problem_id=problem_id)

@app.route('/stats')
def dash_general():
	div_bar_submissions_per_month = pl.GRAPH_SUBMISSIONS_PER_MONTHS(db.__cursor)				# Submissions per month / year (in HTML code)
	div_hist_users_elo_distribution = pl.GRAPH_ELO_DISTRIBUTION(db.__cursor, 'Usuarios')		# Users ELO distribution histogram (in HTML code)
	div_hist_problems_elo_distribution = pl.GRAPH_ELO_DISTRIBUTION(db.__cursor, 'Problemas')	# Problems ELO distribution histogram (in HTML code)
	div_bars_tries_till_solved = pl.GRAPH_TRIES_AVERAGE(db.__cursor)

	return render_template('db_stats.html', subm_per_month=div_bar_submissions_per_month, user_distribution=div_hist_users_elo_distribution, 
		problem_distribution=div_hist_problems_elo_distribution, tries_average=div_bars_tries_till_solved)

@app.route('/problems')
def list_problems():
	problems = db.problem_list()
	return render_template('list.html', item_name='Usuarios', item_list=problems, item='problems',
		cols=['ID', 'Titulo', 'Numero de Usuarios que lo han intentado'])

@app.route('/users')
def list_users():
	users = db.user_list()
	return render_template('list.html', item_name='Problemas', item_list=users, item='users', 
		cols=['ID', 'Numero de Problemas intentados', 'Numero de Problemas resueltos'])

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

	"""
	userid = request.form['user_id']
	userELO = request.form['users_elo']
	if userELO =="":
		userELO = 8.0

	db = Database()
	db.insert_user(userid,userELO)
	db.close_conn()
	"""
	return render_template('insert-user-sucess.html', data =0 )
	
if __name__ == '__main__':
	app.run(port=8181, host="0.0.0.0")


