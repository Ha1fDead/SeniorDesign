from DAL import DataAccess;
# Import and init an XBee device
from xbee import XBee,ZigBee
import serial
import sys
import time

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
			print 'Valid ISU Id'
			return True
		else:
			print 'Not a valid ISU Id'
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
		dataToSend = str(locker.Id) + ' OPEN'
		#Grab the start time to determine if we have timedout on locker acking us
		startTime = time.time()
		print 'Checking Start Time: ' + str(startTime)
		#While we have not received an ack, we haven't timed out, then continue to send
		while not receivedAckOrTimedout:
			#send data
			self.ser.write(dataToSend)
			print 'Sent: ' + dataToSend
			#Is there any data waiting?
			if(self.ser.inWaiting() > 0):
				print 'Data is waiting'
				print self.ser.read()
				#do read logic here

				#Have we timed out?
			else:
				print 'No data is waiting, checking timeout'

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
		print 'You are now in administrative mode'
		txt = raw_input('Type something cool\n')
		return True


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
