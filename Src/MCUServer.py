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
		dal = DataAccess()
		dal.InitializeDB()


		#self.port = '/dev/tty.usbserial-A6007wOm'
		self.port = '/dev/ttyUSB0'
		self.baud = 19200
		self.ServerPanID = '3332'
		self.Timeout = 5

		print 'Port: ' + self.port
		print 'Baud Rate: ' + str(self.baud)

		try:
			self.ser = serial.Serial(self.port, self.baud, timeout=self.Timeout)
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

	def Run(self):	
		xbeeDest = '\x00\x00'
		shouldExit = False

		while not shouldExit:

			#initialize loop variables
			receivedAckOrTimedout = False

			txt = raw_input('Please swipe your ISU IdCard\n')

			print 'Your card number is: ' + txt
			print 'Sending message until we get an Ack or we timeout'

			#Grab the start time to determine if we have timedout on locker acking us
			startTime = time.time()
			print 'Checking Start Time: ' + str(startTime)

			#While we have not received an ack, we haven't timed out, then continue to send
			while not receivedAckOrTimedout:

				#send data
				self.ser.write(txt)
				print 'Sent: ' + txt

				#Is there any data waiting?
				if(self.ser.inWaiting() > 0):
					print self.ser.read()

				#Have we timed out?
				if((time.time() - startTime) > 10):
					print 'TImeout Occured'
					receivedAckOrTimedout = True
				else:
					try:
						#sleep
						time.sleep(0.333)
					except KeyboardInterrupt:
						receivedAckOrTimedout = True
						shouldExit = True
						break;


		self.xbee.halt()
		self.ser.close()
		sys.exit()

if __name__ == "__main__":
	main()
