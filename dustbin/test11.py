from __future__ import print_function

import time, numpy, sys
from Camera import Camera
import cv2
import cv2.cv as cv

captureWidth = 1280 #Width of camera picture
captureHeight = 720 #Height of camera picture
cameraID = 2 #Which camera to use

cam = Camera(cameraID, captureWidth, captureHeight, 2)
transformationMatrix = numpy.array([[2.82259237e+01, 6.24776063e+01, -5.49726821e+04], [ -3.12753244e+01, 5.64481465e+01, -1.36139199e+04], [  1.47719421e-03, -1.51581973e-01, 1.00000000e+00]])

try:
	while True:
		img = cam.getFrame()
		dst = cv2.warpPerspective(img, transformationMatrix, (720,720), flags=cv2.INTER_NEAREST)
		cv2.imshow("Mask", dst)
		cv2.waitKey(50)
except:
	cam.release()
