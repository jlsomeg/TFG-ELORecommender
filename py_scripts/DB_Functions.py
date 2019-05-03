import pymysql
import time
from py_scripts import ELO
from py_scripts import ACR_Globals

#__conn = pymysql.connect(host='localhost', database='acr_dat', user='root', password='')
__conn = pymysql.connect(host='acr-mysql', database='acr_dat', user='user', password='password')
__cursor = __conn.cursor()

try:
	__cursor.execute("ALTER TABLE submission DROP FOREIGN KEY Submission_ibfk_2")
except:
	pass

def insert_user(user_id, elo):
	try:
		__cursor.execute("INSERT INTO user_scores (user_id, elo_global) VALUES ({}, {})".format(user_id, elo))
		__conn.commit()
	except Exception as e:
		print(e)
		raise RuntimeError('El usuario ya existe en la BD')

def insert_problem(problem_id, elo, title):
	try:
		__cursor.execute("INSERT INTO problem (internalId, title) VALUES ({}, '{}')".format(problem_id, title))
		__cursor.execute("INSERT INTO problem_scores (problem_id, elo_global) VALUES ({}, {})".format(problem_id, elo)) #check later
		__conn.commit()
	except Exception as e:
		print(e)
		raise RuntimeError('El problema ya existe en la BD')

def user_submissions(user_id):
	__cursor.execute("SELECT problem_id, status, submissionDate FROM submission WHERE user_id={} ORDER BY submissionDate DESC LIMIT 30".format(user_id))
	return __cursor.fetchall()

def problem_list():
	__cursor.execute("SELECT internalId, title FROM problem ORDER BY internalId ASC")
	return __cursor.fetchall()

def user_list():
	__cursor.execute("""SELECT user_id, COUNT(DISTINCT(problem_id)), SUM(CASE 
							WHEN status = 'AC' THEN 1 
							WHEN status = 'PE' THEN 1 
							ELSE 0 END) FROM submission 
							GROUP BY user_id 
							ORDER BY user_id ASC""")
	return __cursor.fetchall()

def insert_submission(user_id, problem_id, language, status):

	# Checks if both user and problem exists
	__cursor.execute("SELECT * FROM User_Scores WHERE user_id = {}".format(user_id))

	if __cursor.fetchone() is None:
		raise RuntimeError('El usuario no existe en la BD')

	__cursor.execute("SELECT * FROM Problem_Scores WHERE problem_id = {}".format(problem_id))

	if __cursor.fetchone() is None:
		raise RuntimeError('El problema no existe en la BD')

	# Checks if the user already solved the problem
	__cursor.execute("""SELECT user_id, problem_id FROM submission 
		WHERE user_id = {} 
		AND problem_id = {}
		AND (status = 'AC' or status = 'PE')
		GROUP BY user_id, problem_id""".format(user_id, problem_id))

	already_solved = __cursor.fetchone()
	if already_solved is not None:
		raise RuntimeError('El usuario ya ha resuelto este problema')

	# Gets the number of tries
	__cursor.execute("""SELECT COUNT(id), user_id, problem_id FROM submission 
		WHERE user_id = {} 
		AND problem_id = {}
		GROUP BY user_id, problem_id""".format(user_id, problem_id))

	tries = __cursor.fetchone()
	if tries is not None:
		tries = (tries[0] + 1) % ACR_Globals.__MAX_TRIES
	else:
		tries = 1

	# Checks if the user has switched problems
	__cursor.execute(""" SELECT user_id, problem_id, status FROm submission 
		WHERE user_id = {}
		ORDER BY id DESC
		LIMIT 1""".format(user_id))

	gave_up = False
	row = __cursor.fetchone()
	if row is not None:
		if row[2] not in ('AC', 'PE'):
			last_problem = row[1]
			if row[1] != problem_id:
				gave_up = True


	if gave_up or status == 'AC' or tries == 0:
		if gave_up:
			# Checks the number of tries of the previous problem
			__cursor.execute("""SELECT COUNT(id), user_id, problem_id FROM submission 
				WHERE user_id = {} 
				AND problem_id = {}
				GROUP BY user_id, problem_id""".format(user_id, last_problem))

			prev_tries = __cursor.fetchone()
			prev_tries = (prev_tries[0] + 1) % ACR_Globals.__MAX_TRIES
			simulate_fight(user_id, last_problem, language, status, 10 if prev_tries == 0 else prev_tries)
			
		if status == 'AC' or tries == 0:
			simulate_fight(user_id, problem_id, language, status, 10 if tries == 0 else tries)
	
	else:
		__cursor.execute("""INSERT INTO submission (user_id, problem_id, language, status, submissionDate) 
		VALUES ({}, {}, '{}', '{}', '{}')""".format(user_id, problem_id, language, status, time.strftime('%Y-%m-%d %H:%M:%S')))

		__conn.commit()
	
def simulate_fight(user_id, problem_id, language, status, tries):
	# Get ELO from user if exists
	__cursor.execute("SELECT elo_global FROM User_Scores WHERE user_id = {}".format(user_id))

	old_user_elo = __cursor.fetchone()
	if old_user_elo is None:
		raise RuntimeError('El usuario no existe en la BD')
	else:
		old_user_elo = old_user_elo[0]

	# Get ELO from problem if exists
	__cursor.execute("SELECT elo_global FROM Problem_Scores WHERE problem_id = {}".format(problem_id))

	old_problem_elo = __cursor.fetchone()
	if old_problem_elo is None:
		raise RuntimeError('El problema no existe en la BD')
	else:
		old_problem_elo = old_problem_elo[0]

	# Simulate fight
	new_user_elo, new_problem_elo = ELO.SIMULATE(old_user_elo, old_problem_elo, status, tries)

	__cursor.execute("SELECT categoryId FROM problemcategories WHERE problemId = {}".format(problem_id))
	for cat in __cursor.fetchall():
		try:
			category = ACR_Globals.__CATEGORIES[cat[0]]
			__cursor.execute("SELECT {} FROM User_Scores WHERE user_id = {}".format(category, user_id))
			Old_Category_ELO = __cursor.fetchone()[0]
			New_Category_ELO, _ = ELO.SIMULATE(Old_Category_ELO, old_problem_elo, status, tries)
			
			# Update category ELOs
			__cursor.execute("UPDATE User_Scores SET {} = {} WHERE user_id = {}".format(category, New_Category_ELO, user_id))
		except:
			pass

	# Insert into submission table
	__cursor.execute("""INSERT INTO submission (user_id, problem_id, language, status, user_elo, problem_elo, submissionDate) 
		VALUES ({}, {}, '{}', '{}', {}, {}, '{}')""".format(user_id, problem_id, language, status, new_user_elo, new_problem_elo, time.strftime('%Y-%m-%d %H:%M:%S')))

	# Update ELOs on score tables
	__cursor.execute("UPDATE User_Scores SET elo_global = {} WHERE user_id = {}".format(new_user_elo, user_id))
	__cursor.execute("UPDATE Problem_Scores SET elo_global = {} WHERE problem_id = {}".format(new_problem_elo, problem_id))
	
	__conn.commit()