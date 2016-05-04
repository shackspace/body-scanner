from __future__ import print_function

import time, numpy, sys, time
from Camera import Camera
import cv2
import cv2.cv as cv
import serial

captureWidth = 1280 #Width of camera picture
captureHeight = 720 #Height of camera picture
cameraID = 0 #Which camera to use
transformationMatrix = numpy.array([[2.82259237e+01, 6.24776063e+01, -5.49726821e+04], [ -3.12753244e+01, 5.64481465e+01, -1.36139199e+04], [  1.47719421e-03, -1.51581973e-01, 1.00000000e+00]]) #Put in the transformation vectors calculated by test10.py here
laserTreshold = 10 #Tune for best point results


'''
cam = Camera(cameraID, captureWidth, captureHeight, 2)

ser = serial.Serial("/dev/ttyUSB0", 9600)
time.sleep(2)
ser.write("u") #This command will be lost
ser.write("r") #Reset the axis
'''

def detect_dots(img):
	#img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	#ret, img = cv2.threshold(img, laserTreshold, 255, cv2.THRESH_BINARY)
	#img = cv2.GaussianBlur(img,(3,3),0)
	laplacian = cv2.Laplacian(img,cv2.CV_64F)
	cv2.imshow("Mask", laplacian)
	cv2.waitKey(0)
	
	#contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	cv2.drawContours(img, contours, -1, (0,255,0), 3)	
	cv2.imshow("Mask", img)
	cv2.waitKey(0)
	
	
	

def preprocess(img):
	ret, img = cv2.threshold(img, laserTreshold, 255, cv2.THRESH_TOZERO) #Remove noise

	#Mask out everything thats not in the capture range
	cropImage = cv2.imread("crop_image.png", 0)	
	#img = cv2.bitwise_and(img, img, mask=cropImage)
	cv2.imshow("Masked", img)
	cv2.waitKey(0)

	#Build an image that contains the maxima of each column
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	
	maxima = img.argmax(axis=0)
	print(maxima)

	maximaImg = numpy.zeros((len(img[0]), len(img), 1), numpy.uint8)
	numpy.rot90(maximaImg) #Lets us iterate over the columns of the original image
	i = 0
	while i < len(maximaImg):
		maximaImg[i][maxima[i]] = 255
		i += 1
	
	return cv2.flip(numpy.rot90(maximaImg, -1), 1)

img = cv2.imread('testlaser11.png')
img = preprocess(img)
print(img)
cv2.imshow("Masked", img)
cv2.waitKey(0)
img = cv2.warpPerspective(img, transformationMatrix, (720,720), flags=cv2.INTER_NEAREST)
cv2.imshow("Masked", img)
cv2.waitKey(0)
detect_dots(img)

'''
try:
	while True:
		img = cam.getFrame()
		dst = cv2.warpPerspective(img, transformationMatrix, (720,720), flags=cv2.INTER_NEAREST)
		
		cv2.imshow("Mask", dst)
		cv2.waitKey(50)
except:
	cam.release()
'''
