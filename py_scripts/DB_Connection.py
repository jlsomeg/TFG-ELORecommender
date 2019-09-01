import pymysql

class database():

	def __init__(self):
		#self.conn = pymysql.connect(host='localhost', database='acr_dat3', user='root', password='')
		self.conn = pymysql.connect(host='acr-mysql', database='acr_dat', user='user', password='password')
		self.cursor = self.conn.cursor()

	def close(self):
		self.conn.close()

	def query(self, q, fetchall=False, fetchone=False, commit=False):
		self.cursor.execute(q)
		if fetchall: 
			return self.cursor.fetchall()
		elif fetchone:
			return self.cursor.fetchone()
		elif commit:
			self.conn.commit()

	def change_elo_type(self, new_value):
		self.cursor.execute("UPDATE elo_type SET elo_type={}".format(new_value))
		self.conn.commit()