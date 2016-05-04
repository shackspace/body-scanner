from __future__ import print_function

import time, numpy, sys
from Camera import Camera
import cv2
import cv2.cv as cv

captureWidth = 1280 #Width of camera picture
captureHeight = 720 #Height of camera picture
cameraID = 2 #Which camera to use
laserTreshold = 100 #Tune this value for laser detection

cam = Camera(cameraID, captureWidth, captureHeight)

def countdown(duration, event=""):
	#raw_input("(Press Enter to continue)")
	for i in range(duration, 0, -1):
		print(str(i) + " ", end="")
		sys.stdout.flush()
		time.sleep(1)
	print(event)
	
try:
	#Gather the setup vectors
	print("Shooting initial difference picture")	
	baseImg = cam.getFrame()
	baseImgChannelB, baseImgChannelG, baseImgChannelR = cv2.split(baseImg)

	cv2.imshow("Mask", baseImgChannelR)
	cv2.waitKey(0)

	for corner in range(1, 5):
		print("Laser corner " + str(corner) + " and press a button")
		channelB, channelG, channelR = cv2.split(cam.getFrame())
		mask = cv2.absdiff(baseImgChannelB, channelR)

		cv2.imshow("Mask", mask)
		cv2.waitKey(0)	
		ret, mask = cv2.threshold(mask, laserTreshold, 255, cv2.THRESH_BINARY)
	
		if corner == 1: maskCombined = mask 
		else: maskCombined = maskCombined + mask #Add all the dots to a single mask

	maskCombined = cv2.dilate(maskCombined, None, iterations=2) 
	cv2.imshow("Mask", maskCombined)
	cv2.waitKey(0)

	contours, hierarchy = cv2.findContours(maskCombined, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	cv2.drawContours(baseImg, contours, -1, (0,255,0), 3)
	#Find all dots that might be our markers
	trackdots = []
	for contour in contours:
		(x,y), radius = cv2.minEnclosingCircle(contour)
		center = (int(x),int(y))
		radius = int(radius)
		trackdots.append({"radius": radius, "center": center})

	sourceMatrix = []
	for dot in trackdots:
		cv2.circle(baseImg , dot["center"], dot["radius"],(255,255,255), 2) #Visial feedback
		sourceMatrix.append([dot["center"][0], dot["center"][1]])

	cv2.imshow("Mask", baseImg)
	cv2.waitKey(0)	

	pts2 = [[0,0],[0,720],[720,0],[720,720]]
	try:
		transformationMatrix = cv2.getPerspectiveTransform(numpy.float32(sourceMatrix),numpy.float32(pts2))
	except cv2.error:
		cam.release()
		sys.exit("Not enough tracking points found")
		
	print("Your coefficients are")
	print(transformationMatrix)
	dst = cv2.warpPerspective(baseImg, transformationMatrix , (720,720), flags=cv2.INTER_NEAREST)

	cv2.imshow("Mask", dst)
	cv2.waitKey(0)
	cam.release()

except KeyboardInterrupt:
	cam.release()
