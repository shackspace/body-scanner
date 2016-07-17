import time, numpy, sys, socket, struct
import threading
import cv2
import cv2.cv as cv

class ImageClient:
	def receiverThread(self, hostIP, hostPort):	
		imageClientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print("Connecting to Image Server @ " + hostIP + ":" + str(hostPort))
		imageClientSock.connect((hostIP, hostPort))
		print("Connected to Image Server")
		while True:
			st = time.time()
			imageLength = struct.unpack(">I", imageClientSock.recv(4))[0] #Get the 4 byte length prefix
			if imageLength == 0: #If len is 0 the server has stopped sending
				self.receiving = False
				break
				
			sliceNr = struct.unpack(">I", imageClientSock.recv(4))[0] #Get the 4 byte sliceNr
			recvData = ""
			while len(recvData) < (imageLength-8192): 
				recvData += imageClientSock.recv(8192) #Append the packet
			while len(recvData) != imageLength:	recvData += imageClientSock.recv(imageLength-len(recvData)) #Receive the rest
		
			self.imageQueue.append((sliceNr, cv2.imdecode(numpy.fromstring(recvData, numpy.uint8), cv2.CV_LOAD_IMAGE_COLOR)))
			print(str(1/(time.time()-st)) +  "fps")
	
	def getFrame(self, includeFramecounter=False):
		if includeFramecounter: return self.imageQueue.pop(0) #Return the tuple including the framecount
		else: return self.imageQueue.pop(0)[1] #Return the image only

	def __init__(self, hostIP, hostPort):
		self.receiving = True
		self.imageQueue = []
		t = threading.Thread(target=self.receiverThread, args=(hostIP, hostPort))
		t.start()

