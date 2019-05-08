import pymysql
import time
from py_scripts import ELO
from py_scripts import ACR_Globals

#__conn = pymysql.connect(host='localhost', database='acr_dat3', user='root', password='')
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

def insert_problem(problem_id, elo, title, categories):
	try:
		__cursor.execute("INSERT INTO problem (internalId, title) VALUES ({}, '{}')".format(problem_id, title))
		__cursor.execute("INSERT INTO problem_scores (problem_id, elo_global) VALUES ({}, {})".format(problem_id, elo)) #check later
		for code in categories:
			__cursor.execute("INSERT INTO problemcategories (categoryId, problemId) VALUES ({}, {})".format(code, problem_id))
		__conn.commit()
	except Exception as e:
		print(e)
		raise RuntimeError('El problema ya existe en la BD')

def user_submissions(user_id):
	__cursor.execute("SELECT problem_id, status, submissionDate FROM submission WHERE user_id={} ORDER BY submissionDate DESC LIMIT 30".format(user_id))
	return __cursor.fetchall()

def problem_latest_submissions(problem_id):
	__cursor.execute("SELECT user_id, status, submissionDate FROM submission WHERE problem_id={} ORDER BY submissionDate DESC LIMIT 30".format(problem_id))
	return __cursor.fetchall()

def problem_list():
	__cursor.execute("""SELECT pb.internalId, pb.title, COUNT(sb.id)
		FROM problem pb LEFT JOIN submission sb
		ON pb.internalId = sb.problem_id
		GROUP BY pb.internalId
		ORDER BY internalId ASC""")

	prob_list = __cursor.fetchall()

	__cursor.execute("""SELECT ps.problem_id, 
							(SUM(CASE 
							WHEN su.status = 'AC' THEN 1 
							WHEN su.status = 'PE' THEN 1 
							ELSE 0 END) / COUNT(su.id))*100, 
							(SUM(CASE 
							WHEN su.status = 'AC' THEN 1 
							WHEN su.status = 'PE' THEN 1 
							ELSE 0 END) / COUNT(DISTINCT(su.user_id)))*100
						FROM problem_scores ps, submission su
						WHERE ps.problem_id = su.problem_id
						GROUP BY ps.problem_id
						ORDER BY ps.problem_id ASC""")

	problems_ac = __cursor.fetchall()

	return prob_list, problems_ac

def user_list():
	__cursor.execute("""SELECT user_scores.user_id, COUNT(DISTINCT(submission.problem_id)), SUM(CASE 
							WHEN submission.status = 'AC' THEN 1 
							WHEN submission.status = 'PE' THEN 1 
							ELSE 0 END) 
							FROM submission RIGHT JOIN user_scores ON submission.user_id = user_scores.user_id
							GROUP BY user_scores.user_id 
							ORDER BY user_scores.user_id ASC""")

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

def get_easiest_problems():
	easy_problems = []
	problems_ac = []
	for code in ACR_Globals.__CATEGORIES:
		__cursor.execute("""SELECT pc.problemId, pb.title, ps.elo_global
					FROM problemcategories pc, problem_scores ps, problem pb
					WHERE pc.categoryId = {}
					AND pc.problemId = ps.problem_id
					AND pc.problemId = pb.internalId
					ORDER BY ps.elo_global ASC
					LIMIT 5""".format(code))

		p_ids = []
		for prob in __cursor.fetchall():
			easy_problems.append((prob[0], prob[1], ACR_Globals.__CATEGORIES_READABLE[ACR_Globals.__CATEGORIES[code]], prob[2]))
			p_ids.append(str(prob[0]))

		__cursor.execute("""SELECT ps.problem_id, SUM(CASE 
							WHEN su.status = 'AC' THEN 1 
							WHEN su.status = 'PE' THEN 1 
							ELSE 0 END) / COUNT(su.id), SUM(CASE 
							WHEN su.status = 'AC' THEN 1 
							WHEN su.status = 'PE' THEN 1 
							ELSE 0 END) / COUNT(DISTINCT(su.user_id))
					FROM problem_scores ps, submission su
					WHERE ps.problem_id = su.problem_id
					AND ps.problem_id in ({})
					GROUP BY ps.problem_id
					ORDER BY ps.elo_global ASC
					LIMIT 5""".format(','.join(p_ids)))

		for prob in __cursor.fetchall():
			problems_ac.append((prob[0], prob[1]*100, prob[2]*100))

	return easy_problems, problems_ac

def RECOMMENDATIONS(user_id):
	__cursor.execute("SELECT * FROM user_scores WHERE user_id = {}".format(user_id))
	ELOS = __cursor.fetchone()

	CATEGORY_CODES = []
	CATEGORY_FIELD_NAMES = []
	for k,v in ACR_Globals.__CATEGORIES.items():
		CATEGORY_CODES.append(k)
		CATEGORY_FIELD_NAMES.append(v)

	ELOS_PER_CATEGORY = {}
	RECOMMENDATIONS_PER_CATEGORY = {}
	for i, score in enumerate(ELOS[2:]):
		if score != 8.0:
			ELOS_PER_CATEGORY[CATEGORY_FIELD_NAMES[i]] = score
			RECOMMENDATIONS_PER_CATEGORY[CATEGORY_FIELD_NAMES[i]] = []

	ELOS_PER_CATEGORY['Global'] = ELOS[1]
	RECOMMENDATIONS_PER_CATEGORY['Global'] = []

	for CTGRY, ELO_SCORE in ELOS_PER_CATEGORY.items():
		if CTGRY != 'Global':
			CODE = CATEGORY_CODES[CATEGORY_FIELD_NAMES.index(CTGRY)]
			CATEGORIES_RECOMMENDATION(1, user_id, ELO_SCORE, CODE)
		else:
			GLOBAL_RECOMMENDATION(1, user_id, ELO_SCORE)

		for P in __cursor.fetchall():
			RECOMMENDATIONS_PER_CATEGORY[CTGRY].append((P[0], P[1]))

	RECOMMENDATIONS_LIST = []
	for CTGRY, RECO_LIST in RECOMMENDATIONS_PER_CATEGORY.items():
		if CTGRY == 'Global':
			CATEGORY_TITLE = CTGRY
		else:
			CATEGORY_TITLE = ACR_Globals.__CATEGORIES_READABLE[CTGRY]

		for RECO in RECO_LIST:
			__cursor.execute(""" SELECT pb.internalId, pb.title, ps.elo_global 
				FROM problem pb, problem_scores ps
				WHERE ps.problem_id = pb.internalId 
				AND pb.internalId = {}""".format(RECO[0]))

			prb = __cursor.fetchone()
			
			PROBLEM_ID = prb[0]
			PROBLEM_TITLE = prb[1]
			PROBLEM_SCORE = prb[2]
			RECOMMENDATIONS_LIST.append((PROBLEM_ID, PROBLEM_TITLE, CATEGORY_TITLE, PROBLEM_SCORE))

	return RECOMMENDATIONS_LIST

def GLOBAL_RECOMMENDATION(r_type, user_id, user_elo):

	if r_type == 1:
		query = """SELECT problem_id, ABS({} - elo_global) as diff FROM problem_scores
			WHERE problem_id NOT IN (
				SELECT DISTINCT(problem_id) FROM submission
				WHERE user_id = {}
				AND (status = 'AC' or status = 'PE')
				GROUP BY problem_id
			)
			ORDER BY diff ASC LIMIT {}""".format(user_elo, user_id, ACR_Globals.__NUM_RECOMD)
	elif r_type == 2:
		query = """SELECT problem_id, ABS({} - elo_global) as diff FROM problem_scores
			WHERE elo_global >= {}
			AND problem_id NOT IN (
				SELECT DISTINCT(problem_id) FROM submission
				WHERE user_id = {}
				AND (status = 'AC' or status = 'PE')
				GROUP BY problem_id
			)
			ORDER BY diff ASC LIMIT {}""".format(user_elo, user_elo, user_id, ACR_Globals.__NUM_RECOMD)
	
	__cursor.execute(query)

def CATEGORIES_RECOMMENDATION(r_type, user_id, user_elo, code):
	
	if r_type == 1:
		query = """SELECT problem_id, ABS({} - elo_global) as diff FROM problem_scores 
			WHERE problem_id IN (
				SELECT problem_id FROM problemcategories
				WHERE categoryId = {})
			AND problem_id NOT IN (
				SELECT DISTINCT(problem_id) FROM submission
				WHERE user_id = {}
				AND (status = 'AC' or status = 'PE')
				GROUP BY problem_id	)
			ORDER BY diff ASC LIMIT {}""".format(user_elo, code, user_id, ACR_Globals.__NUM_RECOMD)
	elif r_type == 2:
		query = """SELECT problem_id, ABS({} - elo_global) as diff FROM problem_scores 
			WHERE elo_global >= {} 
			AND problem_id IN (
				SELECT problem_id FROM problemcategories
				WHERE categoryId = {})
			AND problem_id NOT IN (
				SELECT DISTINCT(problem_id) FROM submission
				WHERE user_id = {}
				AND (status = 'AC' or status = 'PE')
				GROUP BY problem_id	)
			ORDER BY diff ASC LIMIT {}""".format(user_elo, user_elo, code, user_id, ACR_Globals.__NUM_RECOMD)
	
	__cursor.execute(query)