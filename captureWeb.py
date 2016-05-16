from __future__ import print_function

import time, numpy, sys, time
from Camera import Camera
import cv2
import cv2.cv as cv
import threading
from StepperDriver import StepperDriver
from flask import Flask, send_from_directory

captureWidth = 1280 #Width of camera picture
captureHeight = 720 #Height of camera picture

laserThreshold = 12 #Tune for best point results (12 for Logitech)
sliceCount = 800
imageQueue = [] #Queue for the threads to fetch images from
objString = "" #The final objfile that will be writte

#Read the caloibration Matrix
try: transformationMatrix = numpy.loadtxt("calibration.txt")
except: transformationMatrix = None

stepper = StepperDriver()
stepper.goUp() #Some movement to show the scanner is ready

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

@app.route("/")
def get_index(): return send_from_directory("index.html")

@app.route("index.js")
def get_index_js(): return send_from_directory("index.js")

@app.route("stylesheet.css")
def get_css(): return send_from_directory("stylesheet.css")

@app.route("camera")
def get_camera(): return send_from_directory("camera.html")

@app.route("camera.js")
def get_camera_js(): return send_from_directory("camera.js")

@app.route("api/up", methods=["PUT"])
def put_up():
	global stepper
	stepper.goUp()

@app.route("api/down", methods=["PUT"])
def put_down():
	global stepper
	stepper.goDown()
	
@app.route("api/bottom", methods=["PUT"])
def put_down():
	global stepper
	stepper.goBottom()

@app.route("api/top", methods=["PUT"])
def put_top():
	global stepper
	stepper.goTop()

@app.route("api/scan", methods=["PUT"])
def put_scan():
	global stepper
	
	objString = ""
	stepperThread = threading.Thread(target=stepper.goTop).start() #Start the upwards movement
	scanning = True
	cam = Camera(captureWidth, captureHeight, 120) #Up to 120 images will be held in the cache before discarding images from the cache
	
	#Start image computation threads
	threading.Thread(target=processThread, args=(transformationMatrix, laserThreshold, cam)).start()
	threading.Thread(target=processThread, args=(transformationMatrix, laserThreshold, cam)).start()

	st = time.time()
	while stepperThread.is_alive(): time.sleep(1) #Wait for the scan to finish
	scanning = False #Kill the threads
	f = open("test.obj", "w")
	f.write(objString)
	f.close()
	cam.release()

if __name__ == "__main__":
	app.run()
