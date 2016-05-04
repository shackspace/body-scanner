from __future__ import print_function

import time, numpy, sys
from Camera import Camera
import cv2
import cv2.cv as cv

captureWidth = 1280
captureHeight = 720
cameraID = 1

#Tune this values to have the mask set up right
lower = (55, 80, 60)
upper = (130, 255, 255)

cam = Camera(cameraID, captureWidth, captureHeight)

def countdown(duration, event=""):
	#raw_input("(Press Enter to continue)")
	for i in range(duration, 0, -1):
		print(str(i) + " ", end="")
		sys.stdout.flush()
		time.sleep(1)
	print(event)
	
#Gather the setup vectors
print("Shoot initial difference picture")	
countdown(3, "Got it")
baseImgGrey = cv2.cvtColor(cam.getFrame(), cv2.COLOR_BGR2GRAY)
cv2.imshow("Mask", baseImgGrey)
cv2.waitKey(0)

for corner in range(1, 5):
	print("Laser corner " + str(corner))
	countdown(3, "Got it")
	imgGrey = cv2.cvtColor(cam.getFrame(), cv2.COLOR_BGR2GRAY)
	mask = cv2.absdiff(baseImgGrey, imgGrey)
	cv2.imshow("Mask", mask)
	cv2.waitKey(0)	
	ret, mask = cv2.threshold(mask, 100, 255, cv2.THRESH_BINARY)
	
	if corner == 1: maskCombined = mask 
	else: maskCombined = maskCombined + mask #Add all the dots to a single mask

#Find the 4 calibration spots
#img = cv2.imread('testlaser9.png')

#imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2GREY)
#mask = cv2.inRange(imgHSV, lower, upper)
#mask = cv2.erode(mask, None, iterations=1)
maskCombined = cv2.dilate(maskCombined, None, iterations=3) 
cv2.imshow("Mask", maskCombined)
cv2.waitKey(0)

contours, hierarchy = cv2.findContours(maskCombined, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

#Find all dots that might be our markers
trackdots = {}
for contour in contours:
	(x,y), radius = cv2.minEnclosingCircle(contour)
	center = (int(x),int(y))
	radius = int(radius)
	trackdots[radius] = center

#Get the 4 largest markers and save them
radia = []
for radius, (x, y) in trackdots.items():
	radia.append(radius)
radia.sort()
radia = radia[-4:]	
sourceMatrix = []
for radius in radia:
	cv2.circle(baseImgGrey ,trackdots[radius], radius,(255,255,255), 2) #Visial feedback
	sourceMatrix.append([trackdots[radius][0], trackdots[radius][1]])

cv2.imshow("Mask", baseImgGrey)
cv2.waitKey(0)	

pts2 = [[0,0],[720,0],[0,720],[720,720]]
transformationMatrix = cv2.getPerspectiveTransform(numpy.float32(sourceMatrix),numpy.float32(pts2))
print("Your coefficients are")
print(transformationMatrix)
dst = cv2.warpPerspective(baseImgGrey, transformationMatrix , (720,720), flags=cv2.INTER_NEAREST)

cv2.imshow("Mask", dst)
cv2.waitKey(0)
cam.release()
