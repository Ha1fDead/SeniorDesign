import sqlite3

class DataAccess:

	def __init__(self):

	def InitializeDB:
		connection = sqlite3.connect('../S1525Database.db')
		cursor = connection.cursor()
		cursor.execute('''
			CREATE TABLE locker
			(int lockerId, string lockerName, string lockerPass)
			''')
		cursor.execute('''
			CREATE TABLE users
			(int studentId, int fkLockerId)
			'''
		connection.close()

	def GetLocker(self, Id):

	def GetUser(self, Id):
