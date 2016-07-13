from __future__ import print_function
from flask import Flask, Response, send_from_directory
import time, numpy, sys
from Camera import Camera
import cv2
import cv2.cv as cv
#from StepperDriver import StepperDriver
from ImageServer import ImageServer

app = Flask(__name__)

def go_top_then_stop_image_server(stepperDriver, imageServer):
	stepperDriver.goTop()
	imageServer.stopServer()

@app.route("/api/scan")
def start_scan():
	global captureWifth, captureHeight
	s.goBottom()
	imageServer = ImageServer.ImageServer(captureWidth=captureWidth, captureHeight=captureHeight, buffersize=60)
	while imageServer.isReady() == False: time.sleep(0.01) #Wait for the server to ramp up
	threading.Thread(target=go_top_then_stop_image_server, args=(s, imageServer).start() #Go to top in the background, then stop the image server
	return "started" #Return so the client knows that he can start reveiving images

@app.route("/api/calibrate/start")
def calibrate_wrapper():
	def countdown(duration, event=""):
		for i in range(duration, 0, -1):
			yield str(i) + " "
			time.sleep(1)
		yield event

	def calibrate():
		captureWidth = 1280 #Width of camera picture
		captureHeight = 720 #Height of camera picture
		laserTreshold = 100 #Tune this value for laser detection (100 for Logitech)
		cam = Camera(captureWidth, captureHeight)
		yield "<pre>"
		yield "Resetting axis...\n"
		s.goUp()
		s.goBottom()
		
		#Gather the setup vectors
		yield "Shooting initial difference picture \n"
		baseImg = cam.getFrame()	
		baseImgChannelB, baseImgChannelG, baseImgChannelR = cv2.split(baseImg)
	
		sourceMatrix = []
		
		for corner in range(1, 5):
			edgeFound = False
			while not edgeFound:
				yield "Laserpoint " + str(corner) + "'d edge\n"
				countdown(3, "Picture taken")
				channelB, channelG, channelR = cv2.split(cam.getFrame())
				mask = cv2.absdiff(baseImgChannelB, channelR)

				ret, mask = cv2.threshold(mask, laserTreshold, 255, cv2.THRESH_BINARY)
				mask = cv2.dilate(mask, None, iterations=2) 
		
				contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
				cv2.drawContours(baseImg, contours, -1, (0,255,0), 3)		
		
				cv2.imwrite("calibration_corner" + corner + ".png", baseImg)
		
				if len(contours) > 1:
					yield "More than one edge found, please repeat this edge"
				
				elif len(contours) == 0:
					yield "No edge found, please repeat this edge"
				
				else:
					contour = contours[0]#Select the first and hopefully only recognized contour
					(x,y), radius = cv2.minEnclosingCircle(contour)
					center = (int(x),int(y))
					radius = int(radius)
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
		yield str(transformationMatrix)
		dst = cv2.warpPerspective(baseImg, transformationMatrix , (720,720), flags=cv2.INTER_NEAREST)

		cv2.imwrite("calibration_final.png", dst)
	
		yield "Writing transformation matrix...\n"
		numpy.savetxt("calibration.txt", transformationMatrix)
		cam.release()
		
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
	
@app.route("/api/stepper/down")
def stepper_down():
	global s
	s.goDown()
	
@app.route("/api/stepper/top")
def stepper_top():
	global s
	s.goTop()

@app.route("/api/stepper/bottom")
def stepper_bottom():
	global s
	s.goBottom()
	
@appr.route("/api/stepper/sleep")
def stepper_sleep():
	global s
	s.startSleep()

#s = StepperDriver() #Initialize the Stepper
if __name__ == '__main__':
	app.run()

s = StepperDriver()