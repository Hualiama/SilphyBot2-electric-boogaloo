from datetime import date
from sqlite3 import Cursor
from typing import Callable, Tuple
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.extras import DictCursor

import psycopg2 as pg
import discord
import slog


class Database:
	def __init__(self, user, pss, database, port='5342', host='localhost'):
		self.username = user
		self.password = pss
		self.port = port
		self.database = database
		self.host = host
	
	def connect_and_execute(self, fun: Callable[[Cursor], list]) -> Tuple[bool, list]:
		"""Creates a connection to the database and calls fun with the cursor as a parameter.
		Returns True on success, False on error."""
		cursor = None
		connection = None
		success = True
		ret = []
		
		try:
			connection = pg.connect(user=self.username,
			                        password=self.password,
			                        host=self.host,
			                        port=self.port,
			                        database=self.database)
			connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
			cursor = connection.cursor(cursor_factory=DictCursor)

			ret = fun(cursor)
		except pg.Error as error:
			slog.error(f"Error accessing database: {error}")
			success = False
		finally:
			if cursor:
				cursor.close()
				
			if connection:
				connection.close()
			
		return success, ret
	
	def user_has_entry(self, user: discord.User) -> bool:
		def data_inter(cursor: Cursor):
			sql = f"SELECT * FROM {StrikeConsts.STRIKE_TABLE} WHERE id=%(uid)s LIMIT 1;"
			cursor.execute(sql, {'uid': user.id})
			return [cursor.fetchone() is not None]
		
		return self.connect_and_execute(data_inter)[1][0]
	
	def create_default_strike_entry(self, user: discord.User):
		"""Creates an entry for user with 0 strikes if the user does not have an entry"""
		
		def data_interaction(cur: Cursor):
			sql = f"INSERT INTO {StrikeConsts.STRIKE_TABLE} ({StrikeConsts.ID}, {StrikeConsts.USERNAME}, {StrikeConsts.STRIKE_COUNT}) " \
			      f"VALUES (%(id)s, %(username)s, %(count)s);"
			
			params = {
				'id': user.id,
				'username': f'{user.display_name}#{user.discriminator}',
				'count': 0
			}
			
			cur.execute(sql, params)
			
			return []
		
		if not self.user_has_entry(user):
			self.connect_and_execute(data_interaction)
	
	def add_strike(self, user: discord.User, moderator: discord.User, reason: str, severity: int) -> int:
		"""Adds a strike for user with the specified reason. The date is set to when this method was called.
		
		:param severity: The severity of the infraction
		:param user: The user to strike
		:param moderator: The moderator who issued the strike
		:param reason: The reason for the strike
		:returns: The number of strikes user now has"""
		
		timestamp = date.today()
		
		self.create_default_strike_entry(user)
		
		def data_interaction(cursor: Cursor):
			sql = f"SELECT * FROM {StrikeConsts.STRIKE_TABLE} WHERE id=%s LIMIT 1;"
			cursor.execute(sql, (user.id,))
			result = cursor.fetchone()
			
			strikes = int(result[StrikeConsts.STRIKE_COUNT])
			uname = result[StrikeConsts.USERNAME]
			
			if strikes >= 3 or strikes < 0:
				slog.error(f"Error adding strike! Strikes are already at {strikes}! Check the database.")
				return [strikes]
			
			reason_col = StrikeConsts.get_column(strikes, StrikeConsts.REASON)
			date_col = StrikeConsts.get_column(strikes, StrikeConsts.DATE)
			mod_col = StrikeConsts.get_column(strikes, StrikeConsts.MODERATOR)
			severity_col = StrikeConsts.get_column(strikes, StrikeConsts.SEVERITY)
			
			sql = f"UPDATE {StrikeConsts.STRIKE_TABLE} " \
			      f"SET {StrikeConsts.STRIKE_COUNT}=%(strike_count)s, {StrikeConsts.USERNAME}=%(username)s, {StrikeConsts.LAST_USERNAME}=%(last_user)s, " \
			      f"{reason_col}=%(reason)s, {date_col}=%(date)s, {mod_col}=%(moderator)s, {severity_col}=%(severity)s " \
			      f"WHERE id=%(id)s;"
			
			params = {
				'id': user.id,
				'strike_count': strikes + 1,
				'reason': reason,
				'date': timestamp,
				'moderator': moderator.id,
				'severity': severity,
				'username': f"{user.display_name}#{user.discriminator}",
				'last_user': uname
			}
			
			cursor.execute(sql, params)
			
			return [strikes + 1]
			
		res = self.connect_and_execute(data_interaction)

		return res[1][0]
	
	def remove_strike(self, user: discord.User, position: int) -> int:
		"""Removes a strike from a user. Returns the new number of strikes they have."""
		if not self.user_has_entry(user):
			return -1
		
		def data_inter(cursor: Cursor):
			sql = f"SELECT * FROM {StrikeConsts.STRIKE_TABLE} WHERE {StrikeConsts.ID}=%s;"
			cursor.execute(sql, (user.id,))
			result = cursor.fetchone()
			strike_count = int(result[StrikeConsts.STRIKE_COUNT])
			
			if strike_count == 1:
				self.remove_user(user)
				return [0]
			
			if position <= 0 or position > 3:
				return [-3]
			elif position > strike_count:
				return [-2]
			
			strikes = []
			
			for strike_pref in StrikeConsts.STAGES:
				stk = {
					'reason': result[strike_pref + StrikeConsts.REASON],
					'moderator': result[strike_pref + StrikeConsts.MODERATOR],
					'date': result[strike_pref + StrikeConsts.DATE],
					'severity': result[strike_pref + StrikeConsts.SEVERITY]
				}
				
				strikes.append(stk)
				
			del strikes[position-1]
			
			empty = {
					'reason': None,
					'moderator': None,
					'date': None,
					'severity': None
			}
			
			strikes.append(empty)
			
			sql = f"UPDATE {StrikeConsts.STRIKE_TABLE} SET {StrikeConsts.STRIKE_COUNT}=%s, "
			params = [strike_count - 1]

			for i, ind in zip(StrikeConsts.STAGES, [0, 1, 2]):
				for j, jnd in zip(StrikeConsts.STRIKE_DATA, [0, 1, 2, 3]):
					sql += f"{i + j}=%s"
					
					if not (ind == 2 and jnd == 3):
						sql += ","
					
					sql += " "
					
					params.append(strikes[ind][j])
					
			sql += f"WHERE {StrikeConsts.ID}=%s;"
			params.append(user.id)
			
			cursor.execute(sql, tuple(params))
			
			return [strike_count - 1]
		
		return self.connect_and_execute(data_inter)[1][0]
		
	def remove_user(self, user: discord.User) -> bool:
		"""Removes user from the Database."""
		if not self.user_has_entry(user):
			return False
		
		def data_interaction(cur: Cursor):
			sql = f"DELETE FROM {StrikeConsts.STRIKE_TABLE} WHERE id=%s;"
			cur.execute(sql, (user.id,))
			
			return [True]
			
		return self.connect_and_execute(data_interaction)[1][0]
		

# Constants
class StrikeConsts:
	STRIKE_TABLE = 'strikes'
	
	STRIKE_ONE = 'strike_one_'
	STRIKE_TWO = 'strike_two_'
	BAN = 'ban_'
	
	DATE = 'date'
	REASON = 'reason'
	MODERATOR = 'moderator'
	SEVERITY = 'severity'
	
	STAGES = [STRIKE_ONE, STRIKE_TWO, BAN]
	STRIKE_DATA  = [DATE, REASON, MODERATOR, SEVERITY]
	
	ID = 'id'
	USERNAME = 'username'
	LAST_USERNAME = 'last_username'
	STRIKE_COUNT = 'strike_count'
	
	STRIKE_ONE_REASON = STRIKE_ONE + REASON
	STRIKE_TWO_REASON = STRIKE_TWO + REASON
	BAN_REASON = BAN + REASON
	
	STRIKE_ONE_MODERATOR = STRIKE_ONE + MODERATOR
	STRIKE_TWO_MODERATOR = STRIKE_TWO + MODERATOR
	BAN_MODERATOR = BAN + MODERATOR
	
	STRIKE_ONE_DATE = STRIKE_ONE + DATE
	STRIKE_TWO_DATE = STRIKE_TWO + DATE
	BAN_DATE = BAN + DATE
	
	STRIKE_ONE_SEVERITY = STRIKE_ONE + SEVERITY
	STRIKE_TWO_SEVERITY = STRIKE_TWO + SEVERITY
	BAN_SEVERITY = BAN + SEVERITY

	# Severity consts
	SEVERITY_LOW = 'minor'
	SEVERITY_MEDIUM = 'moderate'
	SEVERITY_HIGH = 'severe'
	INVALID_SEVERITY = -1

	@staticmethod
	def get_col_prefix(strikes):
		if strikes == 0:
			return StrikeConsts.STRIKE_ONE
		elif strikes == 1:
			return StrikeConsts.STRIKE_TWO
		elif strikes == 2:
			return StrikeConsts.BAN
		else:
			return "ERROR"
	
	@staticmethod
	def get_column(strikes: int, data_type: str):
		return StrikeConsts.get_col_prefix(strikes) + data_type

	@staticmethod
	def get_severity(severity: str) -> int:
		severity = severity.lower()
		
		if severity == StrikeConsts.SEVERITY_LOW:
			return 1
		elif severity == StrikeConsts.SEVERITY_MEDIUM:
			return 2
		elif severity == StrikeConsts.SEVERITY_HIGH:
			return 3
		else:
			return -1
