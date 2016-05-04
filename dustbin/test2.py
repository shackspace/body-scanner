from PIL import Image
import numpy

redChannel = Image.open("testlaser8.png").split()[0]

pb = [(382, 571), (785, 569), (409, 425), (706, 430)] #Sourcemap
pa = [(382, 571), (785, 569), (382, 571-403), (785, 569-403)] #Destmap

def find_coeffs(pa, pb):
    matrix = []
    for p1, p2 in zip(pa, pb):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0]*p1[0], -p2[0]*p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1]*p1[0], -p2[1]*p1[1]])

    A = numpy.matrix(matrix, dtype=numpy.float)
    B = numpy.array(pb).reshape(8)

    res = numpy.dot(numpy.linalg.inv(A.T * A) * A.T, B)
    return numpy.array(res).reshape(8)

width, height = redChannel.size
	
redChannel.transform((width, height), Image.PERSPECTIVE, find_coeffs(pa, pb), Image.NEAREST).show()

