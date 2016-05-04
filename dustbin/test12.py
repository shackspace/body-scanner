from __future__ import print_function

import time, numpy, sys
from Camera import Camera
import cv2
import cv2.cv as cv
import serial

img = cv2.imread("testlaser10.png", 1)

B, G, R = cv2.split(img)

cv2.imshow("Mask", R-B)
cv2.waitKey(0)
