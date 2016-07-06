from __future__ import print_function

import time, numpy, sys, time
from Camera import Camera
import cv2
import cv2.cv as cv
import threading
from StepperDriver import StepperDriver

captureWidth = 1280 #Width of camera picture
captureHeight = 720 #Height of camera picture

laserThreshold = 12 #Tune for best point results (12 for Logitech)
sliceCount = 800
imageQueue = [] #Queue for the threads to fetch images from
objString = "" #The final objfile that will be writte

#Read the caloibration Matrix
c = open("calibration.txt", "r")
transformationMatrix = 	numpy.loadtxt("calibration.txt")

def preprocess(img, laserThreshold):
	B, G, img = cv2.split(img) #Select the red channel only 
	ret, img = cv2.threshold(img, laserThreshold, 255, cv2.THRESH_TOZERO) #Remove noise
	
	#Mask out everything thats not in the capture range
	cropImage = cv2.imread("crop_image.png", 0)
	img = cv2.bitwise_and(img, img, mask=cropImage)
	return img

def process(img, z):
	#Build an image that contains the maxima of each diagonal
	#And write this information to te obj file as well
	objString = ""
	maximaImg = numpy.zeros((len(img[0]), len(img), 1), numpy.uint8)
	for diagonalNr in range(-719, 720):
		maxPosition = numpy.diagonal(img, offset=diagonalNr).argmax()
		if maxPosition < 5:
			continue
		
		if diagonalNr < 0:
			posX = maxPosition
			posY = abs(diagonalNr)+maxPosition
		else:
			posX = diagonalNr+maxPosition
			posY = maxPosition

		maximaImg[posX][posY] = 255
		objString += "v " + str(posX) + " " + str(z*2) + " " + str(posY) + "\n"
	
	#cv2.imshow("Diagonal Maxima", maximaImg)
	#cv2.waitKey(10)
	return objString

def processThread(transformationMatrix, laserThreshold, cam):
	global objString, scanning
	
	while scanning:
		try: sliceNr, img = cam.getFrame(True) #Get the first image inside the queue including the framenumber
		except IndexError: 
			time.sleep(0.1) #The list was empty, wait for image to appear
			continue #Retry to grab a frame
		
		print("Processing slice " + str(sliceNr))
		img = preprocess(img, laserThreshold)
		img = cv2.warpPerspective(img, transformationMatrix, (720,720), flags=cv2.INTER_LANCZOS4)
		objString += process(img, sliceNr)
		
s = StepperDriver()
print("Resetting axis...")
s.goUp()
s.goBottom() #Reset the axis

try:
	raw_input("Press Enter to start the scanning process")
	objString = ""
	threading.Thread(target=StepperDriver.goTop) #Move to the top while we scan
	scanning = True
	cam = Camera(captureWidth, captureHeight, 120) #Up to 120 images will be held in the cache before discarding images from the cache
	
	#Start image computation threads
	threading.Thread(target=processThread, args=(transformationMatrix, laserThreshold, cam)).start()
	threading.Thread(target=processThread, args=(transformationMatrix, laserThreshold, cam)).start()

	st = time.time()
	while time.time()-st < 40: time.sleep(1) #Wait for the scan to finish
	scanning = False #Kill the threads
	f = open("test.obj", "w")
	f.write(objString)
	f.close()
	cam.release()

except KeyboardInterrupt:
	try: cam.release()
	except: pass
