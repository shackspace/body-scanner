import glob, sys, time, os
if not os.getegid() == 0: sys.exit("Run as root for serial port access.")
from pyA20.gpio import gpio
from pyA20.gpio import port

class StepperDriver:
	def goUp(self):
		gpio.output(self.serialPin1, 0)
		gpio.output(self.serialPin2, 1)
		fireCommand()
			
	def goDown(self):
		gpio.output(self.serialPin1, 0)
		gpio.output(self.serialPin2, 0)
		fireCommand()
		
	def goBottom(self):
		gpio.output(self.serialPin1, 1)
		gpio.output(self.serialPin2, 0)
		fireCommand()

	def goTop(self):
		gpio.output(self.serialPin1, 1)
		gpio.output(self.serialPin2, 1)
		fireCommand()

	def fireCommand(self):
		gpio.output(self.enablePin, 1)		
		time.sleep(0.05) #Wait for the Arduino to read
		gpio.output(self.enablePin, 0)
		while gpio.input(self.statusPin) == 0: time.sleep(0.1) #Wait for the driver to finish
		
	def __init__(self):
		gpio.init()
		
		self.enablePin = port.PA8 #Pin to enable data transfer to the Arduino
		self.serialPin1 = port.PA9 #Serial1 of the Arduino
		self.serialPin2 = port.PA10 #Serial2 of the Arduino
		self.statusPin = port.PA20 #Status Pin of the Arduino
		
		#Configure the Pins
		gpio.setcfg(self.enablePin, gpio.OUTPUT)
		gpio.setcfg(self.serialPin1, gpio.OUTPUT)
		gpio.setcfg(self.serialPin2, gpio.OUTPUT)
		gpio.setcfg(self.statusPin, gpio.INPUT)
		
		#Set all to zero
		gpio.output(self.enablePin, 0)
		gpio.output(self.serialPin1, 0)
		gpio.output(self.serialPin2, 0)
