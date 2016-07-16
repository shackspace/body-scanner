import time, numpy, sys, socket, cPickle, struct
from Camera import Camera
import threading, cv2

class ImageServer:
	def imageServerThread(self, captureWidth, captureHeight, buffersize, bindPort=5010, bindIP="0.0.0.0"):
		cam = Camera(captureWidth, captureHeight, buffersize)
	
		imageServerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		imageServerSock.bind((bindIP, bindPort))
		imageServerSock.listen(1)
		self.serverReady = True
		
		connection, client_address = imageServerSock.accept()
		print("Connection accepted")
	
		while self.serve == True:
			st = time.time()
			try: sliceNr, img = cam.getFrame(True) #Get the first image inside the queue including the framenumber
			except IndexError: 
				time.sleep(0.01) #The list was empty, wait for image to appear
				continue #Retry to grab a frame

			print("Sending slice " + str(sliceNr))	
			ret, img = cv2.threshold(img, 8, 255, cv2.THRESH_TOZERO) #Tresh to help image compression
			ret, img = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 95]) 
		
			connection.send(struct.pack(">I", len(img))) #Send the 4 byte length prefix
			connection.send(struct.pack(">I", sliceNr)) #Send the 4 byte sliceNr
			connection.sendall(img.tostring()) #Send the actual image
		
			print(str(1/(time.time()-st)) + "fps")

		connection.send(struct.pack(">I", 0)) #Send the len prefix as 0 to indicate that sending has finished
		cam.release()
		time.sleep(5) #Give the client some grace time
		connection.close()

	def stopServer(self):
		self.serve = False

	def isReady(self):
		return self.serverReady

	def __init__(self, captureWidth=1280, captureHeight=720, buffersize=1):
		self.serve = True
		self.serverReady = False
		serverThread = threading.Thread(target=self.imageServerThread, args=(captureWidth, captureHeight, buffersize))
		serverThread.start()
		print("Image Server started")
