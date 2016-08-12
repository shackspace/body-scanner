from __future__ import print_function

import time, numpy, sys
from Camera import Camera
import cv2
import cv2.cv as cv

captureWidth = 1280 #Width of camera picture
captureHeight = 720 #Height of camera picture

cam = Camera(captureWidth, captureHeight, BUFFERSIZE=1000) 

raw_input("Press Enter to abort")

cam.release()

