from __future__ import print_function
from flask import Flask, Response, send_from_directory
import time, numpy, sys, threading, subprocess
from CameraPi import Camera
from ScanModule import Scanner
import cv2
import cv2.cv as cv
from StepperDriverArduino import StepperDriver

app = Flask(__name__)

@app.route("/api/scan")
def start_scan():
	def scan():
		global s
		yield "Resetting stepper"
		s.goBottom()
		yield "Starting scan"
		scanner = Scanner(1640, 1232, s)
		return
		
	return Response(scan())

@app.route("/api/live")
def capture():
	cam = Camera(1640, 1232)
	capture = cam.snap()
	cv2.imwrite("capture.jpg", capture)
	return send_from_directory(".", "capture.jpg")

@app.route("/api/calibrate")
def calibrate_wrapper():
	def calibrate():
		captureWidth = 1640 #Width of camera picture
		captureHeight = 1232 #Height of camera picture
		laserTreshold = 100 #Tune this value for laser detection (100 for Logitech)
		cam = Camera(captureWidth, captureHeight)

		yield "Resetting axis...\n"
		s.goUp()
		s.goBottom()
		
		#Gather the setup vectors
		yield "Shooting initial difference picture \n"
		for i in range(4, 0, -1):
			yield str(i) + " \n"
			time.sleep(1)
		baseImg = cam.snap()
		baseImgChannelB, baseImgChannelG, baseImgChannelR = cv2.split(baseImg)
	
		sourceMatrix = []
		
		for corner in range(1, 5):
			edgeFound = False
			while not edgeFound:
				yield "Laserpoint " + str(corner) + "'d edge\n"
				
				for i in range(5, 0, -1):
					yield str(i) + " \n"
					time.sleep(1)
				yield "Picture taken\n"

				channelB, channelG, channelR = cv2.split(cam.snap())
				mask = cv2.absdiff(baseImgChannelB, channelR)

				ret, mask = cv2.threshold(mask, laserTreshold, 255, cv2.THRESH_BINARY)
				mask = cv2.dilate(mask, None, iterations=2) 
		
				contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
				cv2.drawContours(baseImg, contours, -1, (0,255,0), 3)		
		
				cv2.imwrite("calibration_corner" + str(corner) + ".png", baseImg)
		
				if len(contours) > 1:
					yield "More than one edge found, please repeat this edge\n"
				
				elif len(contours) == 0:
					yield "No edge found, please repeat this edge\n"
				
				else:
					contour = contours[0]#Select the first and hopefully only recognized contour
					(x,y), radius = cv2.minEnclosingCircle(contour)
					center = (int(x),int(y))
					radius = int(radius)
					print("Dot found at " + str(center))
					cv2.circle(baseImg , center, radius,(255,255,255), 2) #Visual feedback
					sourceMatrix.append([center[0], center[1]])
					edgeFound = True

		cv2.imwrite("calibration_corners.png", baseImg)
	
		#Resort the matrix to make sure we have a planar projection (no foldings)
		normalizedSource = []
		sourceMatrix = numpy.float32(sourceMatrix)
		normalizedSource.append(sourceMatrix[sourceMatrix.argmax(axis=0)][0]) #Rightmost edge -> Upper right corner
		normalizedSource.append(sourceMatrix[sourceMatrix.argmax(axis=0)][1]) #Lowest edge -> Lower right corner
		normalizedSource.append(sourceMatrix[sourceMatrix.argmin(axis=0)][0]) #Leftmost edge -> Lower left corner
		normalizedSource.append(sourceMatrix[sourceMatrix.argmin(axis=0)][1]) #Highest edge -> Upper left corner

		#Create and save the masking we will use in the second step do filter out unwanted laser dots
		cropImage = numpy.zeros((captureHeight,captureWidth,1), numpy.uint8)
		pts = numpy.array(normalizedSource, numpy.int32)
		pts = pts.reshape((-1,1,2))
		cv2.fillPoly(cropImage,[pts], (255))
		cv2.imwrite("crop_image.png", cropImage)
	
		#Continue with the perspective transformation
		pts2 = [[720,0], [720,720], [0,720], [0,0]]
		try:
			transformationMatrix = cv2.getPerspectiveTransform(numpy.float32(normalizedSource), numpy.float32(pts2))
		except cv2.error:
			cam.release()
			yield "Not enough tracking points found"
			return 
		
		yield "Your coefficients are:\n"
		yield str(transformationMatrix) + "\n"
		dst = cv2.warpPerspective(baseImg, transformationMatrix , (captureHeight,captureHeight), flags=cv2.INTER_NEAREST)
	
		yield "Writing transformation matrix...\n"
		numpy.savetxt("calibration.txt", transformationMatrix)
		
	return Response(calibrate())
	
@app.route("/api/calibrate/matrix")
def sendMatrix():
	return send_from_directory(".", "calibration.txt")

@app.route("/api/calibrate/cropimage")
def sendCropImage():
	return send_from_directory(".", "crop_image.png")

@app.route("/api/stepper/up")
def stepper_up():
	global s
	s.goUp()
	return "ok"
	
@app.route("/api/stepper/down")
def stepper_down():
	global s
	s.goDown()
	return "ok"
	
@app.route("/api/stepper/top")
def stepper_top():
	global s
	s.goTop()
	return "ok"

@app.route("/api/stepper/bottom")
def stepper_bottom():
	global s
	s.goBottom()
	return "ok"
	
@app.route("/api/stepper/sleep")
def stepper_sleep():
	global s
	s.startSleep()
	return "ok"

s = StepperDriver() #Initialize the Stepper

if __name__ == '__main__':
	app.run(host="0.0.0.0", port=80, debug=True, use_reloader=False)
