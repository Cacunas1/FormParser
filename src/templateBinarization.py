import cv2
import os

def binarize(imgFilePath, imgName, outputFilePath, verbose=False):
	'''
	Function to convert input files images into binarized negatives versions
	:param imgFilePath:    string Input image file path, ending with "/"
	:param imgName:        string Input image name (without extension)
	:param outputFilePath: string Path to place output text file
	:param verbose: 	   boolean to print intermediate steps information
						   or not (default False)
	'''
	img_fp = imgFilePath + imgName + ".png"

	if verbose:
		print("Image file path: ", img_fp)
		print("Image folder content: ", os.listdir(imgFilePath))	

	img = cv2.imread(img_fp)
	
	# convert image to grayscale
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	# binarize image
	img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

	# Erase the gray watermark noise
	img[img > 0] = 255

	# invert image
	img = cv2.bitwise_not(img)

	# save image
	out_fp = outputFilePath + imgName + "_binary.png"
	if verbose:
		print("Output file: ", out_fp)
	cv2.imwrite(out_fp, img)
