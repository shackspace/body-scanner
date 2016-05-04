import cv2
import cv2.cv as cv
import numpy

baseImg = cv2.imread("testlaser9.png")

sourceMatrix = numpy.float32([[705,160],[183,276],[618,631],[1225,305]])
pts2 = [[720,0], [720,720], [0,720], [0,0]]

#Map the edges counterclockwise, starting with the upper right corner
normalizedSource = []
normalizedSource.append(sourceMatrix[sourceMatrix.argmax(axis=0)][0]) #Rightmost edge -> Upper right corner
normalizedSource.append(sourceMatrix[sourceMatrix.argmax(axis=0)][1]) #Lowest edge -> Lower right corner
normalizedSource.append(sourceMatrix[sourceMatrix.argmin(axis=0)][0]) #Leftmost edge -> Lower left corner
normalizedSource.append(sourceMatrix[sourceMatrix.argmin(axis=0)][1]) #Highest edge -> Upper left corner

print(normalizedSource)
transformationMatrix = cv2.getPerspectiveTransform(numpy.float32(normalizedSource), numpy.float32(pts2))
dst = cv2.warpPerspective(baseImg, transformationMatrix , (720,720), flags=cv2.INTER_NEAREST)

cv2.imshow("Mask", dst)
cv2.waitKey(0)



