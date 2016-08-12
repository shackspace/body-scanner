import cv2, threading, time, glob, numpy
from io import BytesIO, BlockingIOError

class Camera:
	def getFrame(self, includeFramecounter=False, raw=True):
		#Read a frame from the buffer and return it
		while True:
			newbytes = self.framebuffer.read(1024)
			if len(newbytes) != 0: self.bytes += newbytes
			else: raise EOFError #Signal that the stream has ended
	
			print(len(self.bytes))
			a = self.bytes.find("\xff\xd8")
			b = self.bytes.find("\xff\xd9")
	
			if a!=-1 and b!=-1:
				jpg = self.bytes[a:b+2]
				self.bytes = self.bytes[b+2:]
				print("Beginning: " + " ".join(hex(ord(n)) for n in jpg[:20]))
				print("End: " + " ".join(hex(ord(n)) for n in jpg[-20:]))
				if raw == True: img = cv2.imdecode(numpy.fromstring(jpg, dtype=numpy.uint8), cv2.CV_LOAD_IMAGE_COLOR)
				else: img = jpg
							
				if includeFramecounter: 
					self.framecounter += 1
					return (self.framecounter, img)
				else: return img
			
			
	def __init__(self):
		#Link to camera modes: http://picamera.readthedocs.io/en/release-1.12/fov.html#camera-modes
		self.framebuffer = BytesIO()
		f = open("/home/swieczor/Downloads/toy_plane_liftoff.avi", "rb")
		self.framebuffer.write(f.read())
		self.framebuffer.seek(0)
		self.bytes = ""
		self.streamFinished = False
		
a = Camera()
while True:
	try: 
		frame = a.getFrame()
		cv2.imshow("Frame", frame)
		cv2.waitKey(1)
	except EOFError: break

