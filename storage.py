import psycopg2 as pg


class Database:
	def __init__(self, user, database, host='localhost'):
		self.connection = pg.connect(username=user, database_name=database, hostname=host)
		self.cursor = self.connection.cursor()
