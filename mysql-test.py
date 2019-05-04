from flask import Flask, render_template, request, url_for, flash, redirect
from forms import UserInsertForm, ProblemInsertForm, SubmissionForm
from py_scripts import ACR_Plots as pl
from py_scripts import DB_Functions as db

app = Flask(__name__)
app.config['SECRET_KEY'] = '5404d19eaf645951b91dae10a842be5b'

### Dashes

@app.route('/')
@app.route('/stats')
def dash_general():
	div_bar_submissions_per_month = pl.GRAPH_SUBMISSIONS_PER_MONTHS(db.__cursor)				# Submissions per month / year (in HTML code)
	div_hist_users_elo_distribution = pl.GRAPH_ELO_DISTRIBUTION(db.__cursor, 'Usuarios')		# Users ELO distribution histogram (in HTML code)
	div_hist_problems_elo_distribution = pl.GRAPH_ELO_DISTRIBUTION(db.__cursor, 'Problemas')	# Problems ELO distribution histogram (in HTML code)
	div_bars_tries_till_solved = pl.GRAPH_TRIES_AVERAGE(db.__cursor)

	return render_template('db_stats.html', subm_per_month=div_bar_submissions_per_month, user_distribution=div_hist_users_elo_distribution, 
		problem_distribution=div_hist_problems_elo_distribution, tries_average=div_bars_tries_till_solved)

@app.route('/problem_list')
def list_problems():
	problems = db.problem_list()
	return render_template('list.html', item_name='Problemas activos de la BD', item_list=problems, item='problem',
		cols=['ID', 'Titulo'])

@app.route('/user_list')
def list_users():
	users = db.user_list()
	return render_template('list.html', item_name='Usuarios activos de la BD', item_list=users, item='user', 
		cols=['ID', 'Nº de Problemas intentados', 'Nº de Problemas Resueltos'])

@app.route('/user/<user_id>')
def dash_user(user_id):
	user_submissions = db.user_submissions(user_id)									# List of the user's latest submissions
	div_plot_user_evolution = pl.GRAPH_USERS_EVOLUTION(db.__cursor, user_id)		# User ELO evolution plot (in HTML code)
	div_plot_user_progress = pl.GRAPH_USER_PROBLEM_PROGRESS(db.__cursor, user_id) 	# user problem completion pie chart (in HTML code)
	div_plot_user_categories = pl.GRAPH_USER_CATEGORIES(db.__cursor, user_id) 		# User ELOs per category (in HTML code)
	user_recommendations = db.RECOMMENDATIONS(user_id)

	return render_template('user_dash.html', evolution=div_plot_user_evolution, progress=div_plot_user_progress, 
		categories=div_plot_user_categories, user_id=user_id, user_submissions=user_submissions, cols=['Problema', 'Estado', 'Fecha'],
		user_recommendations=user_recommendations, rec_cols=['ID del Problema', 'Título', 'Categoría', 'Puntuación ELO'])

@app.route('/problem/<problem_id>')
def dash_problems(problem_id):
	last_submissions = db.problem_latest_submissions(problem_id)						# Latest submissions
	fav_language = pl.GRAPH_PROBLEM_LANGUAGES(db.__cursor, problem_id)
	div_plot_problem_evolution = pl.GRAPH_PROBLEMS_EVOLUTION(db.__cursor, problem_id)	# Problem ELO evolution plot (in HTML code)
	div_plot_user_progress = pl.GRAPH_PROBLEM_SOLVE_RATIO(db.__cursor,problem_id)  		# problem completion pie chart (in HTML code)
	return render_template('problem_dash.html', evolution = div_plot_problem_evolution, 
		progress=div_plot_user_progress, problem_id=problem_id, last_submissions=last_submissions, fav_language=fav_language)

### Inserts

@app.route("/insert_user", methods=['GET', 'POST'])
def insert_user():
	form = UserInsertForm()

	if form.validate_on_submit():
		try:
			db.insert_user(form.user.data, form.elo.data)
			flash(f'Usuario con ID {form.user.data} añadido!', 'success')
		except RuntimeError as err:
			flash("ERROR: {}".format(err.args[0]), 'danger')
		finally:
			return redirect(url_for('insert_user'))

	return render_template('insert_user.html', form=form)

@app.route("/insert_problem", methods=['GET', 'POST'])
def insert_problem():
	form = ProblemInsertForm()
	if form.validate_on_submit():
		try:
			db.insert_problem(form.problem.data, form.elo.data, form.title.data, form.categories.data)
			flash(f'Problema con ID {form.problem.data} añadido!', 'success')
		except RuntimeError as err:
			flash("ERROR: {}".format(err.args[0]), 'danger')
		finally:
			return redirect(url_for('insert_problem'))
	return render_template('insert_problem.html', form=form)

### Simulation

@app.route("/submission", methods=['GET', 'POST'])
def simulate_submission():
	form = SubmissionForm()

	if form.validate_on_submit():
		try:
			db.insert_submission(form.user.data, form.problem.data, form.language.data, form.status.data)
			flash(f'Envio realizado con exito!', 'success')
		except RuntimeError as err:
			flash("ERROR: {}".format(err.args[0]), 'danger')
		finally:
			return redirect(url_for('simulate_submission'))

	return render_template('submission.html', form=form)

@app.route("/easiest", methods=['GET', 'POST'])
def list_easiest_problems():
	easiest = db.get_easiest_problems()
	return render_template('list.html', item_name='los problemas más faciles de cada categoría', item_list=easiest, item='problem', 
		cols=['ID', 'Titulo', 'Categoría', 'Puntuación ELO'])

if __name__ == '__main__':
	app.run(port=8181, host="0.0.0.0")
	#app.run(host='127.0.0.1')