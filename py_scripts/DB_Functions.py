import time
from py_scripts import ELO
from py_scripts import DB_Connection
from py_scripts import ACR_Globals

__elo_type = 3

def insert_user(user_id, elo):
	db = DB_Connection.database()
	try:
		db.query("INSERT INTO user_scores (user_id, elo_global) VALUES ({}, {})".format(user_id, elo), commit=True)
		db.close()
	except Exception as e:
		print(e)
		db.close()
		raise RuntimeError('El usuario ya existe en la BD')

def insert_problem(problem_id, elo, title, categories):
	db = DB_Connection.database()
	try:
		db.query("INSERT INTO problem (internalId, title) VALUES ({}, '{}')".format(problem_id, title))
		db.query("INSERT INTO problem_scores (problem_id, elo_global) VALUES ({}, {})".format(problem_id, elo)) # CHECK LATER
		for code in categories:
			db.query("INSERT INTO problemcategories (categoryId, problemId) VALUES ({}, {})".format(code, problem_id))
		db.conn.commit()
		db.close()
	except Exception as e:
		print(e)
		db.close()
		raise RuntimeError('El problema ya existe en la BD')

def user_submissions(user_id):
	db = DB_Connection.database()
	rows = db.query("SELECT problem_id, status, submissionDate FROM submission WHERE user_id={} ORDER BY submissionDate DESC LIMIT 30".format(user_id), fetchall=True)
	db.close()
	return rows

def problem_latest_submissions(problem_id):
	db = DB_Connection.database()
	rows = db.query("SELECT user_id, status, submissionDate FROM submission WHERE problem_id={} ORDER BY submissionDate DESC LIMIT 30".format(problem_id), fetchall=True)
	db.close()
	return rows

def problem_list():
	db = DB_Connection.database()
	prob_list = db.query("""SELECT pb.internalId, pb.title, COUNT(sb.id)
		FROM problem pb LEFT JOIN submission sb
		ON pb.internalId = sb.problem_id
		GROUP BY pb.internalId
		ORDER BY internalId ASC""", fetchall=True)

	problems_ac = db.query("""SELECT ps.problem_id, ps.elo_global, 
									(SUM(CASE 
									WHEN su.status = 'AC' THEN 1 
									WHEN su.status = 'PE' THEN 1 
									ELSE 0 END) / COUNT(su.id))*100, 
									(SUM(CASE 
									WHEN su.status = 'AC' THEN 1 
									WHEN su.status = 'PE' THEN 1 
									ELSE 0 END) / COUNT(DISTINCT(su.user_id)))*100
								FROM problem_scores ps LEFT JOIN submission su
								ON ps.problem_id = su.problem_id
								GROUP BY ps.problem_id
								ORDER BY ps.problem_id ASC""", fetchall=True)

	categories = {}
	for row in db.query("SELECT problemId, categoryId FROM problemcategories ORDER BY problemId ASC", fetchall=True):
		try:
			if row[0] not in categories:
				categories[row[0]] = []
			categories[row[0]].append(ACR_Globals.__CATEGORIES_READABLE[ACR_Globals.__CATEGORIES[row[1]]]) 
		except:
			pass

	db.close()
	return prob_list, problems_ac, categories

def user_list():
	db = DB_Connection.database()
	rows = db.query("""SELECT user_scores.user_id, COUNT(DISTINCT(submission.problem_id)), SUM(CASE 
							WHEN submission.status = 'AC' THEN 1 
							WHEN submission.status = 'PE' THEN 1 
							ELSE 0 END), user_scores.elo_global
							FROM submission RIGHT JOIN user_scores ON submission.user_id = user_scores.user_id
							GROUP BY user_scores.user_id 
							ORDER BY user_scores.user_id ASC""", fetchall=True)

	db.close()
	return rows

def insert_submission(user_id, problem_id, language, status):
	db = DB_Connection.database()

	# Checks if both user and problem exists

	if db.query("SELECT * FROM user_scores WHERE user_id = {}".format(user_id), fetchone=True) is None:
		raise RuntimeError('El usuario no existe en la BD')

	if db.query("SELECT * FROM problem_scores WHERE problem_id = {}".format(problem_id), fetchone=True) is None:
		raise RuntimeError('El problema no existe en la BD')

	# Checks if the user already solved the problem
	already_solved = db.query("""SELECT user_id, problem_id FROM submission 
		WHERE user_id = {} 
		AND problem_id = {}
		AND (status = 'AC' or status = 'PE')
		GROUP BY user_id, problem_id""".format(user_id, problem_id), fetchone=True)

	if already_solved is not None:
		raise RuntimeError('El usuario ya ha resuelto este problema')

	# Gets the number of tries
	tries = db.query("""SELECT COUNT(id), user_id, problem_id FROM submission 
		WHERE user_id = {} 
		AND problem_id = {}
		GROUP BY user_id, problem_id""".format(user_id, problem_id), fetchone=True)

	if tries is not None:
		tries = (tries[0] + 1) % ACR_Globals.__MAX_TRIES
	else:
		tries = 1

	# Checks if the user has switched problems
	gave_up = False
	row = db.query(""" SELECT user_id, problem_id, status FROM submission 
		WHERE user_id = {}
		ORDER BY id DESC
		LIMIT 1""".format(user_id), fetchone=True)

	if row is not None:
		if row[2] not in ('AC', 'PE'):
			last_problem = row[1]
			if row[1] != problem_id:
				gave_up = True

	if gave_up or status == 'AC' or tries == 0:
		if gave_up:

			# Checks the number of tries of the previous problem
			prev_tries = db.query("""SELECT COUNT(id), user_id, problem_id FROM submission 
				WHERE user_id = {} 
				AND problem_id = {}
				GROUP BY user_id, problem_id""".format(user_id, last_problem), fetchone=True)

			prev_tries = (prev_tries[0] + 1) % ACR_Globals.__MAX_TRIES
			simulate_fight(db, user_id, last_problem, language, status, 10 if prev_tries == 0 else prev_tries)
			
		if status == 'AC' or tries == 0:
			simulate_fight(db, user_id, problem_id, language, status, 10 if tries == 0 else tries)
	
	else:
		db.query("""INSERT INTO submission (user_id, problem_id, language, status, submissionDate) 
		VALUES ({}, {}, '{}', '{}', '{}')""".format(user_id, problem_id, language, status, time.strftime('%Y-%m-%d %H:%M:%S')), commit=True)

	db.close()
	
def simulate_fight(db, user_id, problem_id, language, status, tries):

	# Get ELO from user if exists
	old_user_elo = db.query("SELECT elo_global FROM user_scores WHERE user_id = {}".format(user_id), fetchone=True)
	if old_user_elo is None:
		raise RuntimeError('El usuario no existe en la BD')
	else:
		old_user_elo = old_user_elo[0]

	# Get ELO from problem if exists
	old_problem_elo = db.query("SELECT elo_global FROM problem_scores WHERE problem_id = {}".format(problem_id), fetchone=True)
	if old_problem_elo is None:
		raise RuntimeError('El problema no existe en la BD')
	else:
		old_problem_elo = old_problem_elo[0]

	# Simulate fight
	new_user_elo, new_problem_elo = ELO.SIMULATE(old_user_elo, old_problem_elo, status, tries)

	for cat in db.query("SELECT categoryId FROM problemcategories WHERE problemId = {}".format(problem_id), fetchall=True):
		try:
			category = ACR_Globals.__CATEGORIES[cat[0]]
			Old_Category_ELO = db.query("SELECT {} FROM user_scores WHERE user_id = {}".format(category, user_id), fetchone=True)[0]
			New_Category_ELO, _ = ELO.SIMULATE(Old_Category_ELO, old_problem_elo, status, tries)
			
			# Update category ELOs
			db.query("UPDATE user_scores SET {} = {} WHERE user_id = {}".format(category, New_Category_ELO, user_id))
		except:
			pass

	# Insert into submission table
	db.query("""INSERT INTO submission (user_id, problem_id, language, status, user_elo, problem_elo, submissionDate) 
		VALUES ({}, {}, '{}', '{}', {}, {}, '{}')""".format(user_id, problem_id, language, status, new_user_elo, new_problem_elo, time.strftime('%Y-%m-%d %H:%M:%S')))

	# Update ELOs on score tables
	db.query("UPDATE user_scores SET elo_global = {} WHERE user_id = {}".format(new_user_elo, user_id))
	db.query("UPDATE problem_scores SET elo_global = {} WHERE problem_id = {}".format(new_problem_elo, problem_id))
	db.conn.commit()

def get_easiest_problems():
	db = DB_Connection.database()
	easy_problems = []
	problems_ac = []
	for code in ACR_Globals.__CATEGORIES:
		rows = db.query("""SELECT pc.problemId, pb.title, ps.elo_global
					FROM problemcategories pc, problem_scores ps, problem pb
					WHERE pc.categoryId = {}
					AND pc.problemId = ps.problem_id
					AND pc.problemId = pb.internalId
					ORDER BY ps.elo_global ASC
					LIMIT 5""".format(code), fetchall=True)

		p_ids = []
		for prob in rows:
			easy_problems.append((prob[0], prob[1], ACR_Globals.__CATEGORIES_READABLE[ACR_Globals.__CATEGORIES[code]], prob[2]))
			p_ids.append(str(prob[0]))

		rows = db.query("""SELECT ps.problem_id, SUM(CASE 
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
					LIMIT 5""".format(','.join(p_ids)), fetchall=True)

		for prob in rows:
			problems_ac.append((prob[0], prob[1]*100, prob[2]*100))

	db.close()
	return easy_problems, problems_ac

def RECOMMENDATIONS(user_id):
	db = DB_Connection.database()

	ELOS = db.query("SELECT * FROM user_scores WHERE user_id = {}".format(user_id), fetchone=True)

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
			recommendations = CATEGORIES_RECOMMENDATION(db, 1, user_id, ELO_SCORE, CODE)
		else:
			recommendations = GLOBAL_RECOMMENDATION(db, 1, user_id, ELO_SCORE)

		for P in recommendations:
			RECOMMENDATIONS_PER_CATEGORY[CTGRY].append((P[0], P[1]))

	RECOMMENDATIONS_LIST = []
	for CTGRY, RECO_LIST in RECOMMENDATIONS_PER_CATEGORY.items():
		if CTGRY == 'Global':
			CATEGORY_TITLE = CTGRY
		else:
			CATEGORY_TITLE = ACR_Globals.__CATEGORIES_READABLE[CTGRY]

		for RECO in RECO_LIST:
			prb = db.query(""" SELECT pb.internalId, pb.title, ps.elo_global 
				FROM problem pb, problem_scores ps
				WHERE ps.problem_id = pb.internalId 
				AND pb.internalId = {}""".format(RECO[0]), fetchone=True)

			PROBLEM_ID = prb[0]
			PROBLEM_TITLE = prb[1]
			PROBLEM_SCORE = round(prb[2], 3)
			RECOMMENDATIONS_LIST.append((PROBLEM_ID, PROBLEM_TITLE, CATEGORY_TITLE, PROBLEM_SCORE))

	db.close()
	return RECOMMENDATIONS_LIST

def GLOBAL_RECOMMENDATION(db, r_type, user_id, user_elo):

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
	
	return db.query(query, fetchall=True)

def CATEGORIES_RECOMMENDATION(db, r_type, user_id, user_elo, code):
	
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
	
	return db.query(query, fetchall=True)

# ELO CHANGE
def RE_CALCULATE_ELOS(elo_type):
	db = DB_Connection.database()
	start_time = time.time()
	try:
		RESET_ELOS(db)
		CALCULATE_ELOS(db, elo_type)
		db.conn.commit()

		global __elo_type
		__elo_type = elo_type

		print("Time spent calculating ELOs: ", time.time() - start_time, flush=True)
		db.close()
	except Exception as e:
		print(e)
		db.close()
		raise RuntimeError('Ha ocurrido un problema al cambiar el tipo de ELO')

def RESET_ELOS(db):

	# Resets ELO scores (Users)
	db.query("""UPDATE user_scores SET
		elo_global=8.0,
		elo_adhoc=8.0,
		elo_recorr=8.0,
		elo_search=8.0,
		elo_bin_srch=8.0,
		elo_sorting=8.0,
		elo_vrz=8.0,
		elo_dnmc=8.0,
		elo_dyv=8.0,
		elo_bk_trk=8.0,
		elo_space=8.0,
		elo_graph=8.0,
		elo_geo=8.0""")

	# Resets ELO scores (Problems)
	db.query("""UPDATE problem_scores SET elo_global=8.0""")

	# Resets ELO History
	db.query("UPDATE submission SET user_elo=NULL, problem_elo=NULL")
	db.conn.commit()

def CALCULATE_ELOS(db, elo_type):
	current_fights = {}
	tries_per_couple = {}
	dict_user_elo = dict(db.query("SELECT user_id, elo_global FROM user_scores", fetchall=True))
	dict_problem_elo = dict(db.query("SELECT problem_id, elo_global FROM problem_scores", fetchall=True))
	dict_user_categories = {}

	for row in db.query("SELECT * FROM user_scores", fetchall=True):
		categories = {}
		for i, code in enumerate(ACR_Globals.__CATEGORIES):
			categories[code] = row[i+2]
		dict_user_categories[row[0]] = categories
	
	#for row in tqdm(__cursor.fetchall(), desc="Calculating ELOs"):
	for row in db.query("SELECT * FROM submission ORDER BY id ASC", fetchall=True):
		subm_id = row[0]
		p_id = row[1]
		u_id = row[2]
		status = row[5]

		# Checks the Nº of tries
		if (u_id,p_id) not in tries_per_couple:
			tries_per_couple[(u_id,p_id)] = 1
		else:
			tries_per_couple[(u_id,p_id)] += 1

		# Checks if the user hasn't switched problems
		if u_id not in current_fights:
			current_fights[u_id] = p_id	

		# OK
		if elo_type == 1:
			# Checks all conditions that could trigger a simulation (AC/PE, Problem Switch and 10 tries)
			if current_fights[u_id] != p_id or status in ('AC', 'PE'):

				# If he switches
				if current_fights[u_id] != p_id:
					dict_user_elo[u_id], dict_problem_elo[current_fights[u_id]] = CHANGE_ELOS(db, subm_id, u_id, dict_user_elo[u_id], current_fights[u_id], dict_problem_elo[current_fights[u_id]], status, 1, dict_user_categories)
					current_fights[u_id] = p_id

				# If he wins or reaches __MAX_TRIES tries
				if status in ('AC', 'PE') or tries_per_couple[(u_id,p_id)] == ACR_Globals.__MAX_TRIES:			
					if status in ('AC', 'PE'): 
						del current_fights[u_id]
					dict_user_elo[u_id], dict_problem_elo[p_id] = CHANGE_ELOS(db, subm_id, u_id, dict_user_elo[u_id], p_id, dict_problem_elo[p_id], status, 1, dict_user_categories)

		# OK
		elif elo_type == 2:
			# Checks all conditions that could trigger a simulation (AC/PE, Problem Switch and 10 tries)
			if current_fights[u_id] != p_id or status in ('AC', 'PE'):

				# If he switches
				if current_fights[u_id] != p_id:
					dict_user_elo[u_id], dict_problem_elo[current_fights[u_id]] = CHANGE_ELOS(db, subm_id, u_id, dict_user_elo[u_id], current_fights[u_id], dict_problem_elo[current_fights[u_id]], 
						status, tries_per_couple[(u_id,current_fights[u_id])], dict_user_categories)
					current_fights[u_id] = p_id

				# If he wins
				if status in ('AC', 'PE'):			
					del current_fights[u_id]
					dict_user_elo[u_id], dict_problem_elo[p_id] = CHANGE_ELOS(db, subm_id, u_id, dict_user_elo[u_id], p_id, dict_problem_elo[p_id],
						status, tries_per_couple[(u_id,p_id)], dict_user_categories)

		# OK
		elif elo_type == 3:
			
			# Checks all conditions that could trigger a simulation (AC/PE, Problem Switch and 10 tries)
			if current_fights[u_id] != p_id or status in ('AC', 'PE') or (tries_per_couple[(u_id,p_id)] % ACR_Globals.__MAX_TRIES) == 0:

				# If he switches
				if current_fights[u_id] != p_id:
					num_tries = tries_per_couple[(u_id,current_fights[u_id])] % ACR_Globals.__MAX_TRIES if tries_per_couple[(u_id,current_fights[u_id])] % ACR_Globals.__MAX_TRIES != 0 else ACR_Globals.__MAX_TRIES
					
					dict_user_elo[u_id], dict_problem_elo[current_fights[u_id]] = CHANGE_ELOS(db, subm_id, u_id, dict_user_elo[u_id], current_fights[u_id], dict_problem_elo[current_fights[u_id]], 
						status, num_tries, dict_user_categories)
					
					current_fights[u_id] = p_id

				# If he wins or reaches __MAX_TRIES tries
				if status in ('AC', 'PE') or tries_per_couple[(u_id,p_id)] == ACR_Globals.__MAX_TRIES:			
					if status in ('AC', 'PE'): 
						del current_fights[u_id]
					
					num_tries = tries_per_couple[(u_id,p_id)] % ACR_Globals.__MAX_TRIES if tries_per_couple[(u_id,p_id)] % ACR_Globals.__MAX_TRIES != 0 else ACR_Globals.__MAX_TRIES
					
					dict_user_elo[u_id], dict_problem_elo[p_id] = CHANGE_ELOS(db, subm_id, u_id, dict_user_elo[u_id], p_id, dict_problem_elo[p_id], status,
					 num_tries, dict_user_categories)

	for user,elo in dict_user_elo.items():
		db.query("UPDATE user_scores SET elo_global = {} WHERE user_id = {}".format(elo, user))

	for problem,elo in dict_problem_elo.items():
		db.query("UPDATE problem_scores SET elo_global = {} WHERE problem_id = {}".format(elo, problem))

	for user, elo in dict_user_categories.items():
		db.query("""UPDATE user_scores SET
			elo_adhoc={},
			elo_recorr={},
			elo_search={},
			elo_bin_srch={},
			elo_sorting={},
			elo_vrz={},
			elo_dnmc={},
			elo_dyv={},
			elo_bk_trk={},
			elo_space={},
			elo_graph={},
			elo_geo={}
			WHERE user_id = {}""".format(*elo.values(), user))

def CHANGE_ELOS(db, subm_id, u_id, old_user_elo, p_id, old_problem_elo, status, tries, dict_user_categories):
	new_user_elo, new_problem_elo = ELO.SIMULATE(old_user_elo, old_problem_elo, status, tries)

	for cat in db.query("SELECT categoryId FROM problemcategories WHERE problemId = {}".format(p_id), fetchall=True):
		try:
			dict_user_categories[u_id][cat[0]], _ = ELO.SIMULATE(dict_user_categories[u_id][cat[0]], old_problem_elo, status, tries)
		except:
			pass

	db.query("UPDATE submission SET problem_elo = {}, user_elo = {} WHERE id = {} and user_id = {} and problem_id = {}".format(new_problem_elo, new_user_elo, subm_id, u_id, p_id))
	return new_user_elo, new_problem_elo