import cv2, threading, time, glob

class Camera:
	def captureThread(self, BUFFERSIZE, PRINT_SKIPPED):
		framecounter = 0
		while self.capture:
			s, img = self.cam.read()
			if s:
				if len(self.frameBuffer) == BUFFERSIZE: 
					self.frameBuffer.pop(0)
					if PRINT_SKIPPED: 
						PRINT_SKIPPED=False
					
				self.frameBuffer.append((framecounter, img))
				framecounter += 1
	
	def getFrame(self, includeFramecounter=False, turn=False):
		#Gives back the first frame inside the buffer and removes it from the buffer
		while len(self.frameBuffer) == 0: time.sleep(0.01) #Busywait for a new frame to appear
		frame = self.frameBuffer.pop(0)
		
		#Rotate the image if needed. TODO: Client side implementation for performance reasons
		if turn:
			M = cv2.getRotationMatrix2D((640, 360), 180, 1.0)
			rotated = cv2.warpAffine(frame[1], M, (1280, 720))
			frame = (frame[0], rotated)
			
		if includeFramecounter: return frame #Return the tuple including the framecount
		else: return frame[1] #Only return the image
	
	def bufferLen(self):
		return len(self.frameBuffer)
	
	def release(self):
		print("Releasing camera")
		self.capture = False
		
	def __init__(self, WIDTH, HEIGHT, BUFFERSIZE=1, CAMID=-1, INITTIME=2, PRINT_SKIPPED=True):
		if CAMID == -1:	CAMID = max(map(lambda x: x.split("video")[1], glob.glob("/dev/video*"))) #Find the latest attached system camera
		print("Using camera /dev/video" + CAMID)
		self.cam = cv2.VideoCapture(int(CAMID))
		self.cam.set(3, WIDTH)
		self.cam.set(4, HEIGHT)
		self.capture = True
		self.frameBuffer = []
		self.captureThread = threading.Thread(target=self.captureThread, args=[BUFFERSIZE, PRINT_SKIPPED])
		self.captureThread.start()
		
		time.sleep(INITTIME) #Wait for the camera to warm up (Auto ISO, Whitebalance)
