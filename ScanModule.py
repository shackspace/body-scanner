from __future__ import print_function
import time, numpy, sys, requests, threading
import cv2
import cv2.cv as cv
from CameraPi import Camera

objString = ""
class Scanner:
	def preprocess(self, img, LASER_TRESHHOLD):
	
		B, G, img = cv2.split(img) #Select the red channel only 
		ret, img = cv2.threshold(img, LASER_TRESHHOLD, 255, cv2.THRESH_TOZERO) #Remove noise
	
		#Mask out everything thats not in the capture range
		img = cv2.bitwise_and(img, img, mask=self.cropImage)

		return img

	def process(self, img, z, CAPTURE_HEIGHT):
		#And write this information to te obj file as well
		objString = ""
		for diagonalNr in range(-(CAPTURE_HEIGHT-1), CAPTURE_HEIGHT):
			maxPosition = numpy.diagonal(img, offset=diagonalNr).argmax()
			if maxPosition < 5:
				continue
		
			if diagonalNr < 0:
				posX = maxPosition
				posY = abs(diagonalNr)+maxPosition
			else:
				posX = diagonalNr+maxPosition
				posY = maxPosition

			objString += "v " + str(posX) + " " + str(z*2) + " " + str(posY) + "\n"
		return objString

	def processThread(self, transformationMatrix, LASER_TRESHHOLD, CAPTURE_HEIGHT):
		global objString
		print("Process Thread running")
		while self.cam.readable:
			try: sliceNr, img = self.cam.getFrame(includeFramecounter=True)
			except EOFError: 
				print("Exiting because camera not readable")
				return #All images from the queue were processed

			print("Processing slice " + str(sliceNr))
			img = self.preprocess(img, LASER_TRESHHOLD)
			img = cv2.warpPerspective(img, transformationMatrix, (CAPTURE_HEIGHT, CAPTURE_HEIGHT), flags=cv2.INTER_LANCZOS4) #Make sure we loose as low resolution as possible
			objString += self.process(img, sliceNr, CAPTURE_HEIGHT)

	def __init__(self, CAPTURE_WIDTH, CAPTURE_HEIGHT, STEPPER):
		self.LASER_TRESHHOLD = 40
		self.CAPTURE_WIDTH = 1640
		self.CAPTURE_HEIGHT = 1232
		
		self.transformationMatrix = numpy.loadtxt("calibration.txt") #Get the calibration Matrix
		self.cropImage = cv2.imread("crop_image.png", 0)
		self.cam = Camera(CAPTURE_WIDTH, CAPTURE_HEIGHT)
		self.cam.startCapture()
		STEPPER.goTop()
		self.cam.release()
		print("Waiting for camera to stop recording")
		time.sleep(3)
		
		print("Starting computation threads...")
		t1 = threading.Thread(target=self.processThread, args=(self.transformationMatrix, self.LASER_TRESHHOLD, self.CAPTURE_HEIGHT))
		t2 = threading.Thread(target=self.processThread, args=(self.transformationMatrix, self.LASER_TRESHHOLD, self.CAPTURE_HEIGHT))
		t3 = threading.Thread(target=self.processThread, args=(self.transformationMatrix, self.LASER_TRESHHOLD, self.CAPTURE_HEIGHT))
		
		#Wait for the image computation to finish
		t1.start()
		t2.start()
		t3.start()
		t1.join()
		t2.join()
		t3.join()

		#Write the .obj file
		print("Writing to .obj file test.obj")
		f = open("test.obj", "w")
		f.write(objString)
		f.close()
