import time, numpy
import cv2
import cv2.cv as cv

captureWidth = 1280
captureHeight = 720
cameraID = 0

cam = cv2.VideoCapture(cameraID)
cam.set(3, captureWidth)
cam.set(4, captureHeight)

s, img = cam.read()

if s:
	imgGrey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY);
	ret, imgGrey = cv2.threshold(imgGrey, 150, 255, cv2.THRESH_BINARY)
	circles = cv2.HoughCircles(imgGrey, cv.CV_HOUGH_GRADIENT, 3, 200, param1=100, param2=20, minRadius=50, maxRadius=200)	


	if circles is not None:
		print(circles)
		circles = numpy.round(circles[0, :]).astype("int")
		
		for (x, y, r) in circles:
			# draw the outer circle
			cv2.circle(img, (x, y), r, (0,255,0), 2)
			# draw the center of the circle
			cv2.circle(img, (x, y), r, (0,0,255), 3)

	cv2.imshow('detected circles', img)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

