from __future__ import print_function
import time, numpy, sys, requests, threading
import cv2
import cv2.cv as cv
from ImageClient import ImageClient

HOST = "10.42.23.133"
PORT = 5010
LASER_TRESHHOLD = 12

objString = ""

def preprocess(img, laserThreshold):
	global cropImage #Use the preloaded crop image
	B, G, img = cv2.split(img) #Select the red channel only 
	ret, img = cv2.threshold(img, laserThreshold, 255, cv2.THRESH_TOZERO) #Remove noise
	
	#Mask out everything thats not in the capture range
	img = cv2.bitwise_and(img, img, mask=cropImage)
	return img

def process(img, z):
	#Build an image that contains the maxima of each diagonal
	#And write this information to te obj file as well
	objString = ""
	maximaImg = numpy.zeros((len(img[0]), len(img), 1), numpy.uint8)
	for diagonalNr in range(-719, 720):
		maxPosition = numpy.diagonal(img, offset=diagonalNr).argmax()
		if maxPosition < 5:
			continue
		
		if diagonalNr < 0:
			posX = maxPosition
			posY = abs(diagonalNr)+maxPosition
		else:
			posX = diagonalNr+maxPosition
			posY = maxPosition

		maximaImg[posX][posY] = 255
		objString += "v " + str(posX) + " " + str(z*2) + " " + str(posY) + "\n"
	
	#cv2.imshow("Diagonal Maxima", maximaImg)
	#cv2.waitKey(10)
	return objString

def processThread(transformationMatrix, laserTreshold, imageClient):
	global objString
	while imageClient.receiving or len(imageClient.imageQueue) != 0:
		try: sliceNr, img = imageClient.getFrame(True)
		except IndexError: 
			time.sleep(0.01) #The list was empty, wait for image to appear
			continue #Retry to grab a frame
		
		print("Processing slice " + str(sliceNr))
		img = preprocess(img, laserTreshold)
		img = cv2.warpPerspective(img, transformationMatrix, (720,720), flags=cv2.INTER_LANCZOS4)
		objString += process(img, sliceNr)

#Download the calibration matrix
print("Downloading transformation matrix...")
r = requests.get("http://" + HOST + "/api/calibrate/matrix")
matrix = "\n".join(r.content.split("\n")[0:3]) #Only use the first 3 lines
f = open("calibration.txt","w")
f.write(matrix)
f.close()
transformationMatrix = numpy.loadtxt("calibration.txt")

#Download the crop image
print("Downloading crop image...")
r = requests.get("http://" + HOST + "/api/calibrate/cropimage")
f = open("crop_image.png", "w")
f.write(r.content)
f.close()
cropImage = cv2.imread("crop_image.png", 0)

#Start the scanning, retrieval and computation
print("Starting scanning process...")
r = requests.get("http://" + HOST + "/api/scan")
print("Scanning started, starting retrieval thread...")
imageClient = ImageClient(HOST, PORT)

print("Retrieval started, starting computation threads...")
computationThreads = []
t1 = threading.Thread(target=processThread, args=(transformationMatrix, LASER_TRESHHOLD, imageClient))
t2 = threading.Thread(target=processThread, args=(transformationMatrix, LASER_TRESHHOLD, imageClient))

#Wait for the image computation to finish
t1.daemon = True
t2.daemon = True
t1.start()
t2.start()
t1.join()
t2.join()

#Write the .obj file
print("Writing to .obj file test.obj")
f = open("test.obj", "w")
f.write(objString)
f.close()
