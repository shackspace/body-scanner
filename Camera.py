import cv2, threading, time, glob

class Camera:
	def captureThread(self, BUFFERSIZE):
		try:
			framecounter = 0
			while self.capture:
				s, img = self.cam.read()
				if s:
					if len(self.frameBuffer) == BUFFERSIZE: 
						self.frameBuffer.pop(0)
						print("Discarding Frame")
						
					self.frameBuffer.append((framecounter, img))
					framecounter += 1
							
		except KeyboardInterrupt: self.capture = False
	
	def getFrame(self, includeFramecounter=False):
		#Gives back the first frame inside the buffer and removes it from the buffer
		while len(self.frameBuffer) == 0: time.sleep(0.01) #Busywait for a new frame to appear
		if includeFramecounter: return self.frameBuffer.pop(0) #Return the tuple including the framecount
		else: return self.frameBuffer.pop(0)[1] #Only return the image
	
	def release(self):
		print("Releasing camera")
		self.capture = False
		
	def __init__(self, WIDTH, HEIGHT, BUFFERSIZE=1, CAMID=-1, INITTIME=2):
		if CAMID == -1:	CAMID = max(map(lambda x: x.split("video")[1], glob.glob("/dev/video*"))) #Find the latest attached system camera
		print("Using camera /dev/video" + CAMID)
		self.cam = cv2.VideoCapture(int(CAMID))
		self.cam.set(3, WIDTH)
		self.cam.set(4, HEIGHT)
		self.capture = True
		self.frameBuffer = []
		self.captureThread = threading.Thread(target=self.captureThread, args=[BUFFERSIZE]).start()
		
		time.sleep(INITTIME) #Wait for the camera to warm up (Auto ISO, Whitebalance)
