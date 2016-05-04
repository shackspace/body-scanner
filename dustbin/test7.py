import time, numpy
import cv2
import cv2.cv as cv

captureWidth = 1280
captureHeight = 720
cameraID = 1

#Tune this values to have the mask set up right
lower = (55, 80, 60)
upper = (130, 255, 255)

cam = cv2.VideoCapture(cameraID)
cam.set(3, captureWidth)
cam.set(4, captureHeight)

s, img = cam.read()

#img = cv2.imread('testlaser9.png')
if s:
	imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	mask = cv2.inRange(imgHSV, lower, upper)
	#mask = cv2.erode(mask, None, iterations=1)
	mask = cv2.dilate(mask, None, iterations=3) 
	cv2.imshow("Mask", mask)
	cv2.waitKey(0)
	
	contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	
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
		cv2.circle(img ,trackdots[radius], radius,(255,255,255), 2) #Visial feedback
		sourceMatrix.append([trackdots[radius][0], trackdots[radius][1]])
	
	cv2.imshow("Mask", img)
	cv2.waitKey(0)	
	
	pts2 = [[0,0],[720,0],[0,720],[720,720]]
	transformationMatrix = cv2.getPerspectiveTransform(numpy.float32(sourceMatrix),numpy.float32(pts2))
	dst = cv2.warpPerspective(img, transformationMatrix , (720,720), flags=cv2.INTER_NEAREST)
	
	cv2.imshow("Mask", dst)
	cv2.waitKey(0)	
