import glob, sys, time, os
if not os.getegid() == 0: sys.exit("Run as root for serial port access.")
import RPi.GPIO as GPIO

class StepperDriver:
	def goUp(self):
		GPIO.output(self.serialPin1, GPIO.LOW)
		GPIO.output(self.serialPin2, GPIO.HIGH)
		self.fireCommand()
			
	def goDown(self):
		GPIO.output(self.serialPin1, GPIO.LOW)
		GPIO.output(self.serialPin2, GPIO.LOW)
		self.fireCommand()
		
	def goBottom(self):
		GPIO.output(self.serialPin1, GPIO.HIGH)
		GPIO.output(self.serialPin2, GPIO.LOW)
		self.fireCommand()

	def goTop(self):
		GPIO.output(self.serialPin1, GPIO.HIGH)
		GPIO.output(self.serialPin2, GPIO.HIGH)
		self.fireCommand()

	def fireCommand(self):
		GPIO.output(self.enablePin, GPIO.HIGH)
		time.sleep(0.05) #Wait for the Arduino to read
		GPIO.output(self.enablePin, GPIO.LOW)
		while GPIO.input(self.statusPin) == 0: time.sleep(0.1) #Wait for the driver to finish
		
	def __init__(self):
		GPIO.setmode(GPIO.BOARD)
		
		self.enablePin = 31 #Pin to enable data transfer to the Arduino
		self.serialPin1 = 35 #Serial1 of the Arduino
		self.serialPin2 = 33 #Serial2 of the Arduino
		self.statusPin = 37 #Status Pin of the Arduino
		
		#Configure the Pins
		GPIO.setup(self.enablePin, GPIO.OUT)
		GPIO.setup(self.serialPin1, GPIO.OUT)
		GPIO.setup(self.serialPin2, GPIO.OUT)
		GPIO.setup(self.statusPin, GPIO.IN)
		
		#Set all to zero
		GPIO.output(self.enablePin, GPIO.LOW)
		GPIO.output(self.serialPin1, GPIO.LOW)
		GPIO.output(self.serialPin2, GPIO.LOW)
