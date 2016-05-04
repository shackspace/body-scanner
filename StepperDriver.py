import serial, glob, sys

class StepperDriver:
	def __init__(self):
		try: serialDevice = "/dev/ttyUSB" + max(map(lambda x: x.split("USB")[1], glob.glob("/dev/ttyUSB*")))
		except ValueError: sys.exit("Error: No /dev/ttyUSB device found")
		self.serial = serial.Serial(serialDevice, 9600)

