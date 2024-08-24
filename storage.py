import psycopg2
import slog

class Database:
    def __init__(self, user, password, dbname, port, host):
        self.connection = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            port=port,
            host=host
        )
        self.cursor = self.connection.cursor()

    def query(self, query_string, params=None):
        self.cursor.execute(query_string, params or ())
        return self.cursor.fetchall()

    def execute(self, query_string, params=None):
        self.cursor.execute(query_string, params or ())
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()
