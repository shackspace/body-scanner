from __future__ import print_function

import time, numpy, sys, time
from Camera import Camera
import cv2
import cv2.cv as cv
import serial
from matplotlib import pyplot as plt
import threading

captureWidth = 1280 #Width of camera picture
captureHeight = 720 #Height of camera picture
cameraID = 2 #Which camera to use
transformationMatrix = numpy.array([[  8.33201518e-01,   6.11691846e+00,  -1.01481913e+03], [ -1.47917690e+00,   6.12184890e+00,   4.60088796e+02], [ -3.74309023e-04,   5.88473250e-03,   1.00000000e+00]])
laserTreshold = 12 #Tune for best point results

def preprocess(img):
	B, G, img = cv2.split(img) #Select the red channel only 
	ret, img = cv2.threshold(img, laserTreshold, 255, cv2.THRESH_TOZERO) #Remove noise
	#img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	
	#Mask out everything thats not in the capture range
	cropImage = cv2.imread("crop_image.png", 0)
	print(len(cropImage))
	print(len(img))
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
		objString += "v " + str(posX/10) + " " + str(z*10) + " " + str(posY/10) + "\n"
	
	cv2.imshow("Diagonal Maxima", maximaImg)
	cv2.waitKey(10)
	return objString



cam = Camera(cameraID, captureWidth, captureHeight, 0)
ser = serial.Serial("/dev/ttyUSB0", 9600)
time.sleep(1)
ser.write("u") #This command will be lost
ser.write("r") #Reset the axis
time.sleep(2)
raw_input("Press Enter to start the scanning process")

try:
	objString = ""
	ser.write("t") #Move to the top while we scan
	
	i = 0
	while i < 800:
		print("Scanning slice " + str(i))
		img = cam.getFrame()
		img = preprocess(img)
		img = cv2.warpPerspective(img, transformationMatrix, (720,720), flags=cv2.INTER_LANCZOS4)
		objString += process(img, i)
		i += 1

	f = open("test.obj", "w")
	f.write(objString)
	f.close()
	cam.release()

except KeyboardInterrupt:
	cam.release()
