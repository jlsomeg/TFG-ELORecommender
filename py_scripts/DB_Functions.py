import pymysql

#__conn = pymysql.connect(host='localhost', database='acr_dat', user='root', password='')
__conn = pymysql.connect(host='acr-mysql', database='acr_dat', user='user', password='password')
__cursor = __conn.cursor()

def insert_user(user_id, elo):
	try:
		__cursor.execute("INSERT INTO user_scores (user_id, elo_global) VALUES ({}, {})".format(user_id, elo))
		__conn.commit()
		return True
	except Exception as e:
		print(e)
		return False

def insert_problem(problem_id, elo, title):
	try:
		__cursor.execute("INSERT INTO problem (internalId, title) VALUES ({}, '{}')".format(problem_id, title))
		__cursor.execute("INSERT INTO problem_scores (problem_id, elo_global) VALUES ({}, {})".format(problem_id, elo))
		__conn.commit()
		return True
	except Exception as e:
		print(e)
		return False

def user_submissions(user_id):
	__cursor.execute("SELECT id, problem_id, status, submissionDate FROM submission WHERE user_id={} ORDER BY submissionDate DESC".format(user_id))
	return __cursor.fetchall()

def problem_list():
	__cursor.execute("SELECT internalId, title FROM problem ORDER BY internalId ASC")
	return __cursor.fetchall()

def user_list():
	__cursor.execute("""SELECT u.user_id, COUNT(DISTINCT(s.problem_id)), u.elo_global 
							FROM submission s, user_scores u
							WHERE u.user_id = s.user_id
							GROUP BY user_id 
							ORDER BY user_id ASC""")
	return __cursor.fetchall()