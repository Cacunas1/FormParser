import cv2
import pytesseract as ocr

def txtExtraction(input_image, page=0, verbose=False):
	'''
	Function to extract all text (at once, together) from a medical license
	image to a text file.
	:param input_image: string Input image file path
	:param page:        integer page number (default 0)
	:param verbose:     bool option to print intermediate steps information
						(default False)
	'''
	tempFilePath = "../templates/Medical_License" + str(page) + "_template.png"  
	
	if verbose:
		print("Input Image filepath: "    , input_image)
		print("Template Image filepath: " , tempFilePath)
	
	img = cv2.imread(input_image)
	tem = cv2.imread(tempFilePath)
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	tem = cv2.cvtColor(tem, cv2.COLOR_BGR2GRAY)
	
	# invert image for processing purposes
	img = cv2.bitwise_not(img)
	
	# Threshold the images to have saturated colors
	tem = cv2.threshold(tem, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
	img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
	
	# Subtract the template from the data
	img = cv2.bitwise_and(img, tem)
	
	# Erase the gray watermark noise
	img[img < 255] = 0
	
	# Extract the text
	text = pytesseract.image_to_string(img, lang="spa")
	
	return(text)