import time, numpy
import cv2
import cv2.cv as cv

captureWidth = 1280
captureHeight = 720
cameraID = 1

cam = cv2.VideoCapture(cameraID)
cam.set(3, captureWidth)
cam.set(4, captureHeight)

s, img = cam.read()

if s:
	imgGrey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY);
	imgGrey = (255-imgGrey) #Invert
	
	params = cv2.SimpleBlobDetector_Params()
	print(params)
	# Change thresholds
	params.minThreshold = 0
	params.maxThreshold = 255
	 
	#Filter by Area.
	params.filterByArea = True
	params.minArea = 5000
	params.maxArea = 9999999
		
	#Filter by convex
	params.filterByConvexity = False
	params.filterByInertia = False
	#params.minConvexity = 0.87
	
	
	detector = cv2.SimpleBlobDetector(params)
	keypoints = detector.detect(img)

	print(keypoints)

	imgGrey = cv2.drawKeypoints(imgGrey, keypoints, numpy.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
 
	cv2.imshow('detected circles', imgGrey)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

