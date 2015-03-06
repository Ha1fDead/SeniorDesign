import sqlite3

class DataAccess:

	def __init__(self):

	def InitializeDB(self):
		connection = self.GetConnection()
		cursor = connection.cursor()
		cursor.execute('''
			CREATE TABLE locker
			(lockerId INTEGER PRIMARY KEY, 
			lockerName TEXT, 
			lockerPass TEXT)
		''')
		cursor.execute('''
			CREATE TABLE users
			(studentId INTEGER PRIMARY KEY, 
			FOREIGHN KEY(stuLocker) REFERENCES locker(lockerId))
		''')
		connection.close()

	def GetLocker(self, Id):
		connection = self.GetConnection()
		cursor = connection.cursor()

		cursor.execute('''
			SELECT * FROM TABLE users WHERE lockerId = Id
		''')
		
		locker = cursor.fetchone()

		return locker;

	def GetUser(self, Id):
		

	def GetConnection(self):
		return sqlite3.connect('../S1525Database.db')


