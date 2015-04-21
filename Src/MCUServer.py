from DAL import DataAccess;
# Import and init an XBee device
from xbee import XBee,ZigBee
import signal
import serial
import sys
#used for timing out xbee communication
import time
#used for timing out input
import select

#Handles all of the I/O of the MCU
#loops through to infinite, checking for input
#if input is here, process it
#input can come from user or any of the LCUs
#LID OPEN
#LID ACKN
#LID BATT 6300

def main():
	server = MCUServer()
	server.Run()

class MCUServer:

	def __init__(self):
		print 'Initializing MCU Server'
		print 'Initializing Db access'
		self.dal = DataAccess()
		self.dal.InitializeDB()

		self.port = '/dev/tty.usbserial-A6007wOm'
		#self.port = '/dev/ttyUSB0'
		self.baud = 19200
		self.ServerPanID = '3332'
		self.Timeout = 5
		self.InputTimeout = 60

		print 'Port: ' + self.port
		print 'Baud Rate: ' + str(self.baud)

		try:
			print 'Attempting to initialize serial connection: ' + self.port
			self.ser = serial.Serial(self.port, self.baud, timeout=self.Timeout)

			print 'Attempting to register XBEE'
			self.xbee = XBee(self.ser)

			self.xbee.send('at', command='ID', parameter=self.ServerPanID)
			print 'Set XBee panID to: ' + self.ServerPanID
    
		except Exception, e:
			print 'Could not initialize serial interface.'
			sys.exit()
		else:
			pass
		finally:
			pass

	def CheckForIsuIdCard(self, potentialId):
		print 'Checking: ' + potentialId
		if(potentialId == '60095739208269118=4912120000000000000'):
			return True
		else:
			return False

	def GetLockerOfId(self, isuId):
		user = self.dal.GetUser(isuId)
		if(user is not None):
			locker = self.dal.GetLockerFromId(user.lockerId)
			return locker
		else:
			return None

	def GetLockerOfUser(self, groupUsername, groupPassword):
		locker = self.dal.GetLocker(groupUsername, groupPassword)
		return locker

	def TryToOpenLocker(self, locker):
		receivedAckOrTimedout = False
		dataToSend = str(locker.Id) + ' open\n'
		self.ser.write(dataToSend)

		#Grab the start time to determine if we have timedout on locker acking us
		startTime = time.time()
		#While we have not received an ack, we haven't timed out, then continue to send
		while not receivedAckOrTimedout:
			#Is there any data waiting?
			if(self.ser.inWaiting() > 0):
				print 'Data is waiting'
				print self.ser.read()
				#do read logic here

				#Have we timed out?
			else:
				if((time.time() - startTime) > 10):
					print 'TImeout Occured'
					receivedAckOrTimedout = True
				else:
					try:
						#sleep
						time.sleep(0.333)
					except KeyboardInterrupt:
						receivedAckOrTimedout = True




	def AdministrativeMode(self):
		startTime = time.time()

		hasTimedOutOrFinished = False
		print 'You are now in administrative mode. Type \'quit\' to exit'
		self.PrintHelp()
		while not hasTimedOutOrFinished:
			userInput = self.GetInputWithTimeout(self.InputTimeout)
			if(userInput == None):
				#timeout
				hasTimedOutOrFinished = True

			userInput = str(userInput).split()

			if(userInput[0] == "quit"):
				hasTimedOutOrFinished = True
			elif(userInput[0] == "help"):
				self.PrintHelp()
			elif(userInput[0] == "battery"):
				if(len(userInput) == 2):
					battThreshold = userInput[1]
					lockers = self.dal.GetLockers()
					for locker in lockers:
						if(locker.Battery < battThreshold):
							print 'Id: ' + str(locker.Id) + ' Battery: ' + str(locker.Battery)
			elif(userInput[0] == "users"):
				users = self.dal.GetUsers()
				for user in users:
					print 'Id: ' + str(user.Id) + ' LockerId: ' + str(user.lockerId)
			elif(userInput[0] == "lockers"):
				lockers = self.dal.GetLockers()
				for locker in lockers:
					print 'Id: ' + str(locker.Id) + ' Username: ' + locker.Username + ' Password: ' + locker.Password + ' Battery: ' + str(locker.Battery)
			elif(userInput[0] == "add_locker"):
				if(len(userInput) == 2):
					locker = self.dal.GetLockerFromId(userInput[1])
					if(locker == None):
						createdLocker = self.dal.CreateLocker(userInput[1])
						if(createdLocker == None):
							print 'Could not create locker'
						else:
							print 'Locker created successfully'
					else:
						print 'Locker already exists!'
				else:
					print 'Input parameters not valid!'
			elif(userInput[0] == "add_user"):
				if(len(userInput) == 3):
					locker = self.dal.GetLockerFromId(userInput[2])
					user = self.dal.GetUser(userInput[1])
					if(user == None and locker != None):
						createdUser = self.dal.CreateUser(userInput[1], userInput[2])
						if(createdUser == None):
							print 'Could not create User'
						else:
							print 'User created successfully'
					else:
						print 'Locker does not exist or the user exists!'
				else:
					print 'Input parameters not valid!'
			elif(userInput[0] == "group_user"):
				if(len(userInput) == 3):
					user = self.dal.GetUser(userInput[1])
					locker = self.dal.GetLockerFromId(userInput[2])
					if(user != None and locker != None):
						user.lockerId = locker.Id
						self.dal.UpdateUser(user)
					else:
						print 'That user/locker does not exist!'
					print ''
				else:
					print 'Input Paramaters not valid!'
			elif(userInput[0] == "set_locker"):
				if(len(userInput) == 4):
					locker = self.dal.GetLockerFromId(userInput[1])
					if(locker != None):
						locker.Username = userInput[2]
						locker.Password = userInput[3]
						self.dal.UpdateLocker(locker)
					else:
						print 'That locker does not exist!'
					print ''
				else:
					print 'Input Paramaters not valid!'
			elif(userInput[0] == "remove_user"):
				if(len(userInput) == 2):
					user = self.dal.GetUser(userInput[1])
					if(user != None):
						self.dal.DeleteUser(user)
					else:
						print 'User does not exist!'
				else:
					print 'Input Paramaters not valid!'
			elif(userInput[0] == "remove_locker"):
				if(len(userInput) == 2):
					locker = self.dal.GetLockerFromId(userInput[1])
					if(locker != None):
						users = self.dal.GetUsers()
						for user in users:
							if(user.lockerId == locker.Id):
								user.lockerId = None
								self.dal.UpdateUser(user)
						self.dal.DeleteLocker(locker)
					else:
						print 'Locker does not exist!'
				else:
					print 'Input Paramaters not valid!'
			elif(userInput[0] == "revoke_locker"):
				if(len(userInput) == 2):
					locker = self.dal.GetLockerFromId(userInput[1])
					if(locker != None):
						users = self.dal.GetUsers()
						for user in users:
							if(user.lockerId == locker.Id):
								user.lockerId = None
								self.dal.UpdateUser(user)
				else:
					print 'Input Paramaters not valid!'

			else:
				print 'Command Not Recognized'

		return True

	def PrintHelp(self):
		print 'Helpful Commands'
		print '\'quit\' : Quits the administrative mode, returning to normal operation'
		print '\'help\' : Prints out this help message'
		print '\'battery\' : Prints out the locker ids of all of the lockers with low batteries'
		print '\'users\' : print a list of all user IDs in the system'
		print '\'lockers\' : prints a list of all locker ids in the system'
		print '\'add_locker <lockerId>\' : Adds a locker with the designated id. The Id is to be given to the LCU first, and then sent here'
		print '\'add_user <studentId> <lockerId>\' : adds the user with the given ISU ID # to the provided locker Id'
		print '\'group_user <studentId> <lockerId>\' : Groups the given user to the given locker, so that they can access it'
		print '\'set_locker <lockerId> <groupName> <groupPassword>\' : Sets the given locker to have the given groupName and password'
		print '\'remove_user <studentId>\' : removes the provided user from the system'
		print '\'remove_locker <lockerId> : removes the locker from the system and all references to it from users\''
		print '\'revoke_locker <lockerId> : removes all references to the locker and clears username/password\''

	def GetInputWithTimeout(self, timeout):
		#I have no idea how this works
		print "Please enter your command"
		i, o, e = select.select( [sys.stdin], [], [], timeout )
		if (i):
			txt = sys.stdin.readline().strip()
			return txt
		else:
			return None




	def Run(self):
		shouldExit = False

		while not shouldExit:

			#initialize loop variables
			receivedAckOrTimedout = False

			print 'Please swipe an ISU ID Card or enter your username/password'

			txt = raw_input('Username: ')
			lockerToOpen = None

			if self.CheckForIsuIdCard(txt):
				#check if this id exists in the database, and retrieve the locker it is associated to if so
				lockerToOpen = self.GetLockerOfId(txt)
			else:
				#check if this group username exists in the database or requesting admin access
				username = txt
				password = raw_input('Password: ')

				if(username == 'ADMIN'):
					if(password == 'ADMIN'):
						#this is for demo purposes, in the future (if selling product) put password into a hash that can be changed
						if(self.AdministrativeMode()):
							print 'You successfully left administrative mode'
						else:
							print 'Administrative Mode timed out and you have been logged out'
					else:
						print 'The username/password you entered is Incorrect!'
				else:
					lockerToOpen = self.GetLockerOfUser(username, password)

			#Check if the user existed and had a locker associated with it
			if(lockerToOpen is not None):
				if(self.TryToOpenLocker(lockerToOpen)):
					print 'Locker successfully opened'
				else:
					print 'Locker timed out'
			else:
				print 'ISU ID not accepted or Username/Password incorrect'



		self.xbee.halt()
		self.ser.close()
		sys.exit()

if __name__ == "__main__":
	main()
