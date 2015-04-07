import sqlite3
from locker import Locker
from user import User

class DataAccess:

	def __init__(self):
		print 'Initializing DAL'

	def InitializeDB(self):
		connection = self.GetConnection()
		cursor = connection.cursor()
		cursor.execute('''
			CREATE TABLE if not exists lockers
			(lockerId INTEGER PRIMARY KEY, 
			curGroupName TEXT, 
			curGroupPass TEXT,
			batteryVoltage INTEGER)
		''')
		cursor.execute('''
			CREATE TABLE if not exists users
			(studentId TEXT PRIMARY KEY, 
			stuLockerId INTEGER REFERENCES lockers(lockerId))
		''')
		connection.close()

	def GetLockerFromId(self, Id):
		connection = self.GetConnection()
		cursor = connection.cursor()

		cursor.execute('''
			SELECT * FROM lockers WHERE lockerId = (?)
		''', (Id,))
		
		locker = cursor.fetchone()
		connection.close()

		if(locker is not None):
			locker = Locker(locker)
			return locker

		else:
			return None

	def GetLocker(self, username, password):
		connection = self.GetConnection()
		cursor = connection.cursor()

		cursor.execute('''
				SELECT * FROM lockers WHERE (curGroupName) = ? AND (curGroupPass) = ?
			''', (username,password))

		locker = cursor.fetchone()
		connection.close()
		if(locker is not None):
			locker = Locker(locker)
			return locker
		else:
			return None

	def GetUser(self, Id):
		connection = self.GetConnection()
		cursor = connection.cursor()

		cursor.execute('''
			SELECT * FROM users WHERE studentId = (?)
		''', (Id,))

		user = cursor.fetchone()
		connection.close()

		if(user is not None):
			user = User(user)
			return user
		else:
			return None

	def CreateUser(self, studentId, lockerId):
		#adds a new user with the associated locker
		connection = self.GetConnection()
		cursor = connection.cursor()

		cursor.execute('''
			INSERT INTO users 
				(studentId, stuLockerId) VALUES
				(?, ?)
		''', (studentId, lockerId,))

		connection.commit()
		connection.close()

		return self.GetUser(studentId)

	def CreateLocker(self, Id):
		#adds a new locker with the associated ID
		#the id is also what is used to communicate with locker
		#grab ID from cooking process
		connection = self.GetConnection()
		cursor = connection.cursor()
		cursor.execute('''
			INSERT INTO lockers
				(lockerId,curGroupName,curGroupPass,batteryVoltage) VALUES (?,?,?,?)
		''', (Id,'testing','testing',0))

		connection.commit()
		connection.close()

		return self.GetLockerFromId(Id)

	
	def GetConnection(self):
		return sqlite3.connect('../S1525Database.db')


