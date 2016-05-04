from PIL import Image, ImageDraw, ImageChops
import time, numpy
from scipy.interpolate import Rbf

import pygame, pygame.camera, pygame.image

import matplotlib.pyplot as plt  

width = 1280
height = 1024
radius = 2
stepSize = 128
camera = "/dev/video1"

calibrationImage = Image.new("RGB", (width, height), "black")
draw = ImageDraw.Draw(calibrationImage)

pygame.camera.init()
cam = pygame.camera.Camera(camera, (1280, 720))
cam.start()

def captureImage():
	global cam
	img = cam.get_image()
	return Image.frombytes("RGB", (1280, 720), pygame.image.tostring(img, "RGB", False))

def findBrightest(img):
	grey = img.convert("L")

	maxX = 0
	maxY = 0
	maxV = 0
	
	width, height = grey.size
	for x in range(0, width-1):
		for y in range(0, height-1):
			if grey.getpixel((x,y)) > maxV:
				maxX = x
				maxY = y
				maxV = grey.getpixel((x,y))
	
	print("New spot: %s/%s with value %s" % (maxX, maxY, maxV))
	return (maxX, maxY, maxV)

knownDots = {
	"sensorX": [],
	"sensorY": [],
	"realX": [],
	"realY": []
}

for x in range(stepSize, width-1, stepSize):
	for y in range(stepSize, height-1, stepSize):
		noDotImage = captureImage()
		
		draw.rectangle([(x-radius, y-radius), (x+radius, y+radius)], fill="white")
		calibrationImage.save("calib.png")
		time.sleep(0.2) #Wait for feh to reload the image
		
		diffImage = ImageChops.difference(noDotImage, captureImage())
		maxX, maxY, maxV = findBrightest(diffImage)
		
		if maxV > 50:
			knownDots["sensorX"].append(maxX)
			knownDots["sensorY"].append(maxY)
			knownDots["realX"].append(x)
			knownDots["realY"].append(y)

#At this point we have a sparsely populated matrix 
#Create the sensor matrix
tx = numpy.linspace(0, 1280.0, 1280)  
ty = numpy.linspace(0, 720.0, 720)  
XI, YI = numpy.meshgrid(tx, ty)

#Creating the interpolation function and populating the sensor matrix value 
#FIXME: Do the y values as well
rbf = Rbf(knownDots["sensorX"], knownDots["sensorY"], knownDots["realX"], function="inverse")
ZI = rbf(XI, YI)  

print(ZI)

