import glob, sys, time, os
if not os.getegid() == 0: sys.exit("Run as root for serial port access")
from pyA20.gpio import gpio
from pyA20.gpio import port

class StepperDriver:
	
	def goUp(self, steps=200):
		self.setDirectionUp()
		self.endSleep()
		
		for i in range(0, steps):
			gpio.output(self.stepPin, 1)
			time.sleep(0.008) 
			gpio.output(self.stepPin, 0)
			time.sleep(0.008) 
		
		self.startSleep()
	
	def goBottom(self):
		self.setDirectionDown()
		self.endSleep()
		
		debounce = 0

		for i in range(0, self.height):
			if gpio.input(self.sensorPin) == 0: debounce += 1
			else: debounce = 0
			
			if debounce > 5:
				self.goUp() #Move the sledge out of the sensor
				self.startSleep()
				break
			
			gpio.output(self.stepPin, 1)
			time.sleep(0.001) #1000 Micro
			gpio.output(self.stepPin, 0)
			time.sleep(0.001) #1000 Micro
			
			
			#TODO: Insert magic ramps here
		
		self.startSleep()
				
		
	def startSleep(self): gpio.output(self.sleepPin, 0)
	def endSleep(self): gpio.output(self.sleepPin, 1)
	
	def setDirectionUp(self): gpio.output(self.dirPin, 1)
	def setDirectionDown(self): gpio.output(self.dirPin, 0)
	
		
	def __init__(self):
		gpio.init()
		
		self.sensorPin = port.PA14 #Port for the light barrier on the column bottom
		self.sleepPin = port.PA9 #Sleep Pin of the Polulu
		self.stepPin = port.PA10 #Step Pin of the Polulu
		self.dirPin = port.PA20 #Direction Pin of the Polulu
		
		self.height = 34700
		
		#Configure the Pins
		gpio.setcfg(self.sensorPin, gpio.INPUT)
		gpio.pullup(self.sensorPin, gpio.PULLUP)

		gpio.setcfg(self.sleepPin, gpio.OUTPUT)
		gpio.setcfg(self.stepPin, gpio.OUTPUT)
		gpio.setcfg(self.dirPin, gpio.OUTPUT)
		
		
