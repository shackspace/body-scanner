import time, numpy, sys, socket, cPickle, struct
from Camera import Camera
import threading, cv2

class ImageServer:
	def compressThread(self):
		while self.serve == True:
			while len(self.compressQueue) == 0: time.sleep(0.05) #Wait for an image to appear
			sliceNr, img = self.compressQueue.pop(0)
			ret, img = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 95])
			self.sendQueue.append((sliceNr, img)) #Compress the image and make it ready for sending
		
	def imageServerThread(self, captureWidth, captureHeight, buffersize, bindPort=5010, bindIP="0.0.0.0"):
		cam = Camera(captureWidth, captureHeight, buffersize)
	
		imageServerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		imageServerSock.bind((bindIP, bindPort))
		imageServerSock.listen(1)
		self.serverReady = True
		
		connection, client_address = imageServerSock.accept()
		print("Connection accepted")		
		self.clientConnected = True
	
		while self.serve == True:
			st = time.time()
			try: sliceNr, img = cam.getFrame(includeFramecounter=True, turn=True) #Get the first image inside the queue including the framenumber
			except IndexError: 
				time.sleep(0.01) #The list was empty, wait for image to appear
				continue #Retry to grab a frame

			ret, img = cv2.threshold(img, 8, 255, cv2.THRESH_TOZERO) #Tresh to help image compression (costs no performance)
			self.compressQueue.append((sliceNr, img)) #Put the image in the compression Queue
			
			#Threads compress the image in the background here
			
			while len(self.sendQueue) == 0: time.sleep(0.05) #Wait for an image to enter the send queue
			print("Sending slice " + str(sliceNr))	
			sliceNr, img = self.sendQueue.pop(0) #Get a compressed image from the queue
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

	def __init__(self, captureWidth=1280, captureHeight=720, buffersize=1, compressThreads=3):
		self.serve = True
		self.serverReady = False
		self.clientConnected = False
		self.compressQueue = []
		self.sendQueue = []	
		serverThread = threading.Thread(target=self.imageServerThread, args=(captureWidth, captureHeight, buffersize))
		serverThread.start()
		
		for i in range(0, compressTheads): threading.Thread(target=self.compressThread).start()
		
		print("Image Server started")
