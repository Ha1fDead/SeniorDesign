from DAL import DataAccess;
# Import and init an XBee device
from xbee import XBee,ZigBee
import serial

#Handles all of the I/O of the MCU
#loops through to infinite, checking for input
#if input is here, process it
#input can come from user or any of the LCUs

dal = DataAccess()

dal.InitializeDB()

#dal.AddNewLocker(4)

#dal.GetLocker(1)
#dal.CreateUser(0, 1, False)
#dal.GetUser(0)

#while(1):

	#Check for user input
		#process user input

	#check for LCU input
		#process LCU request	


ser = serial.Serial('/dev/ttyUSB0', 19200)

xbee = XBee(ser)
    
    # Set remote DIO pin 2 to low (mode 4)
#xbee.at(command='EE', parameter='\x00')
#xbee.at(command='KY', parameter='FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF')

while True:
	#ser.write('a');
	txt = raw_input('Please swipe your ISU IdCard\n')

	print 'Your card number is: ' + txt

	xbee.send('tx', dest_addr='\x00\x00', data=txt)
	print 'Sent: ' + txt

#	try:
#		data = xbee.wait_read_frame()
#		print 'Data: ' + data
#
#	except KeyboardInterrupt:
#		break;

ser.close()