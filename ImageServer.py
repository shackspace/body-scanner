import time, numpy, sys, socket, cPickle, struct
from Camera import Camera
import threading, cv2

class ImageServer:
	def fetchThread(self):
		while self.serve == True:
			sliceNr, img = self.cam.getFrame(includeFramecounter=True, turn=True) #Get the first image inside the queue including the framenumber
			ret, img = cv2.threshold(img, 8, 255, cv2.THRESH_TOZERO) #Tresh to help image compression (costs no performance)
			ret, img = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 95])
			self.sendQueue.append((sliceNr, img)) #Compress the image and make it ready for sending
		
	def imageServerThread(self, captureWidth, captureHeight, buffersize, bindPort=5010, bindIP="0.0.0.0"):
		imageServerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		imageServerSock.bind((bindIP, bindPort))
		imageServerSock.listen(1)
		self.serverReady = True
		
		connection, client_address = imageServerSock.accept()
		print("Connection accepted")		
		self.clientConnected = True
	
		while self.serve == True:			
			while len(self.sendQueue) == 0: time.sleep(0.05) #Fetch an image from the send queue
			sliceNr, img = self.sendQueue.pop(0) #Get a compressed image from the queue
			print("Sending slice " + str(sliceNr))	
			connection.send(struct.pack(">I", len(img))) #Send the 4 byte length prefix
			connection.send(struct.pack(">I", sliceNr)) #Send the 4 byte sliceNr
			connection.sendall(img.tostring()) #Send the actual image

		connection.send(struct.pack(">I", 0)) #Send the len prefix as 0 to indicate that sending has finished
		cam.release()
		time.sleep(5) #Give the client some grace time
		connection.close()

	def stopServer(self):
		self.serve = False

	def isReady(self):
		return self.serverReady

	def __init__(self, captureWidth=1280, captureHeight=720, buffersize=1, fetchThreads=3):
		self.serve = True
		self.serverReady = False
		self.clientConnected = False
		self.sendQueue = []	
		serverThread = threading.Thread(target=self.imageServerThread, args=(captureWidth, captureHeight, buffersize))
		serverThread.start()
		
		self.cam = Camera(captureWidth, captureHeight, buffersize)
		for i in range(0, fetchThreads): threading.Thread(target=self.fetchThread).start()
		
		print("Image Server started")
