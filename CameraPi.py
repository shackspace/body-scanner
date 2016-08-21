import cv2, threading, time, glob, numpy
from picamera import PiCamera
from io import BytesIO, BlockingIOError

class Camera:
	def captureThread(self):
		self.cam.start_recording(self.framebuffer, format="mjpeg", quality=95)
		while self.capture: self.cam.wait_recording(1) #Wait for the external interrupt
		self.cam.stop_recording()		
	
	def getFrame(self, includeFramecounter=False, raw=True):
		#Read a frame from the buffer and return it
		while True:
			newbytes = self.framebuffer.read(1024)
			if len(newbytes) != 0: self.bytes += newbytes
			else:
				self.readable = False 
				raise EOFError #Signal that the stream has ended
	
			a = self.bytes.find("\xff\xd8")
			b = self.bytes.find("\xff\xd9")
	
			if a!=-1 and b!=-1:
				jpg = self.bytes[a:b+2]
				self.bytes = self.bytes[b+2:]
				if raw == True: img = cv2.imdecode(numpy.fromstring(jpg, dtype=numpy.uint8), cv2.CV_LOAD_IMAGE_COLOR)
				else: img = jpg
							
				if includeFramecounter: 
					self.framecounter += 1
					return (self.framecounter, img)
				else: return img
	
	def startCapture(self):
		self.capture = True
		self.readable = True
		self.framecounter = 0
		self.bytes = "" #Persistent cache for image slicing
		self.captureThread = threading.Thread(target=self.captureThread)
		self.captureThread.start()
	
	def release(self):
		print("Releasing camera")
		self.capture = False

	def close(self):
		self.cam.close()
	
	def snap(self):
		jpg = BytesIO()
		self.cam.capture(jpg, "jpeg")
		return cv2.imdecode(numpy.fromstring(jpg.getvalue(), dtype=numpy.uint8), cv2.CV_LOAD_IMAGE_COLOR)
		
	def __init__(self, WIDTH=1640, HEIGHT=1232, FRAMERATE=40, ISO=800, INITTIME=2):
		#Link to camera modes: http://picamera.readthedocs.io/en/release-1.12/fov.html#camera-modes
		print("Intializing Camera")
		self.framebuffer = BytesIO()
		self.cam = PiCamera()
		self.cam.resolution = (WIDTH, HEIGHT)
		self.cam.framerate = FRAMERATE
		self.cam.iso = ISO
		self.cam.awb_mode = "off"
		self.cam.awb_gains = (3, 1) #(RED, BLUE), we need more red than blue

		print("Camera warming up")
		time.sleep(INITTIME)
		

