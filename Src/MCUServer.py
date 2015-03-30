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

def main():
	server = MCUServer()
	server.Run()


class MCUServer:

	def __init__(self):
		print 'Initializing MCU Server'
		print 'Initializing Db access'
		dal = DataAccess()
		dal.InitializeDB()


		self.port = '/dev/tty.usbserial-A6007wOm'
		#port = '/dev/ttyUSB0'
		self.baud = 19200

		print 'Port: ' + self.port
		print 'Baud Rate: ' + str(self.baud)

		try:
			self.ser = serial.Serial(self.port, self.baud)
			self.xbee = XBee(self.ser, callback=self.ReceiveData)
    
		except Exception, e:
			print 'Could not initialize serial interface.'
			sys.exit()
		else:
			pass
		finally:
			pass

	def ReceiveData(self, data):
		print data

	def Run(self):	
		xbeeDest = '\x00\x00'
		receivedAck = False
		shouldExit = False

		while not shouldExit:
			txt = raw_input('Please swipe your ISU IdCard\n')

			print 'Your card number is: ' + txt

			print 'Sending message until we get an Ack or we timeout'

			while not receivedAck:
				self.xbee.send('tx', dest_addr=xbeeDest, data=txt)
				print 'Sent: ' + txt

				try:
					time.sleep(0.001)
				except KeyboardInterrupt:
					shouldExit = True
					break;

		self.xbee.halt()
		self.ser.close()
		sys.exit()

if __name__ == "__main__":
	main()
