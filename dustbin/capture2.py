from __future__ import print_function

import time, numpy, sys, time
from Camera import Camera
import cv2
import cv2.cv as cv
import serial
from matplotlib import pyplot as plt

captureWidth = 1280 #Width of camera picture
captureHeight = 720 #Height of camera picture
cameraID = 1 #Which camera to use
transformationMatrix = numpy.array([[  8.96512225e-01, 6.45252878e+00, -1.11436470e+03],[ -1.46524374e+00, 6.18261381e+00, 5.49930990e+02],[ -2.49070722e-04, 5.28223027e-03, 1.00000000e+00]]) #Put in the transformation vectors calculated by test10.py here

laserTreshold = 20 #Tune for best point results

def detect_dots(img, z):
	objString = ""
	pixels = numpy.nditer(img, flags=["multi_index"])
	while not pixels.finished:
		if pixels[0] == 255:
			objString += "v " + str(pixels.multi_index[1]) + " " + str(z) + " " + str(pixels.multi_index[0]) + "\n"
		pixels.iternext()
	
	return objString

def preprocess(img):
	ret, img = cv2.threshold(img, laserTreshold, 255, cv2.THRESH_TOZERO) #Remove noise

	#Mask out everything thats not in the capture range
	cropImage = cv2.imread("crop_image.png", 0)
	img = cv2.bitwise_and(img, img, mask=cropImage)
	
	#cv2.imshow("Cropped", img)
	#cv2.waitKey(0)
	cv2.destroyWindow("Cropped")

	#Build an image that contains the maxima of each column
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	
	maxima = img.argmax(axis=0)
	maximaImg = numpy.zeros((len(img[0]), len(img), 1), numpy.uint8)
	numpy.rot90(maximaImg) #Lets us iterate over the columns of the original image
	i = 0
	while i < len(maximaImg):
		maximaImg[i][maxima[i]] = 255
		i += 1
		
	return cv2.flip(numpy.rot90(maximaImg, -1), 1)


cam = Camera(cameraID, captureWidth, captureHeight, 0)

ser = serial.Serial("/dev/ttyUSB0", 9600)
time.sleep(2)
ser.write("u") #This command will be lost
ser.write("r") #Reset the axis
time.sleep(3)
ser.write("r") #Reset the axis

try:
	objString = ""
	i = 0
	while i < 50:
		print("Scanning slice " + str(i))
		img = cam.getFrame()
		#cv2.imshow("Frame", img)
		#cv2.waitKey(0)
		cv2.destroyWindow("Frame")
		#img = cv2.imread('testlaser11.png')
		img = preprocess(img)
		cv2.imshow("Processed", img)
		cv2.waitKey(0)
		cv2.destroyWindow("Processed")
		img = cv2.warpPerspective(img, transformationMatrix, (720,720), flags=cv2.INTER_NEAREST)
		edges = cv2.Canny(img,100,255)
		#img2 = cv2.warpPerspective(cam.getFrame(), transformationMatrix, (720,720), flags=cv2.INTER_NEAREST)
		cv2.imshow("Warped", img)
		cv2.waitKey(0)
		cv2.destroyWindow("Warped")

		objString += detect_dots(img, i)
		ser.write("u")
		time.sleep(2)
		i += 1

	f = open("test.obj", "w")
	f.write(objString)
	f.close()
	cam.release()

except KeyboardInterrupt:
	cam.release()
