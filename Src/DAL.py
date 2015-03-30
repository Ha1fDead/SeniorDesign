import sqlite3

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
			(studentId INTEGER PRIMARY KEY, 
			stuLockerId INTEGER REFERENCES lockers(lockerId),
			isAdmin BOOLEAN)
		''')
		connection.close()

	def GetLocker(self, Id):
		connection = self.GetConnection()
		cursor = connection.cursor()

		cursor.execute('''
			SELECT * FROM lockers WHERE lockerId = (?)
		''', (Id,))
		
		locker = cursor.fetchone()
		print locker
		connection.close()
		return locker

	def GetUser(self, Id):
		connection = self.GetConnection()
		cursor = connection.cursor()

		cursor.execute('''
			SELECT * FROM users WHERE studentId = (?)
		''', (Id,))

		user = cursor.fetchone()
		print user
		connection.close()
		return user

	def CreateUser(self, studentId, lockerId, isAdmin):
		#adds a new user with the associated locker
		connection = self.GetConnection()
		cursor = connection.cursor()

		cursor.execute('''
			INSERT INTO users 
				(studentId, stuLockerId, isAdmin) VALUES
				(?, ?, ?)
		''', (studentId, lockerId, isAdmin,))

		connection.commit()
		connection.close()

	def AddNewLocker(self, Id):
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

	
	def GetConnection(self):
		return sqlite3.connect('../S1525Database.db')


