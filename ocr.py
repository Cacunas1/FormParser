# import the necessary packages
#%matplotlib inline
from matplotlib import pyplot as plt
from PIL import Image
import pytesseract
#import argparse
import cv2
import os

path = "example_01.png"

# load the example image and convert it to grayscale
image = cv2.imread(path)

plt.imshow(image)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# check to see if we should apply thresholding to preprocess the
# image
gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
plt.imshow(gray)

filename = "gray-output.png"
cv2.imwrite(filename, gray)

text = pytesseract.image_to_string(Image.open(filename))
print(text)