from PIL import Image

redChannel = Image.open("testlaser2.png").split()[0]

width = 800	
height = 600

maxPositions = []

for i in range(0, width-1):
	maxPosition = 0
	for j in range(0, height-1):
		if redChannel.getpixel((i, j)) > maxPosition: maxPosition = j
	maxPositions.append(maxPosition)
		
print(maxPositions)
