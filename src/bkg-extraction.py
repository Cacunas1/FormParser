# import the necessary packages
%matplotlib inline
from matplotlib import pyplot as plt
from PIL import Image
import pytesseract
#import argparse
import cv2
import os

foregnd_fn = "sample.png"
backgnd_fn = "sample-bkg.png"

fg = cv2.imread(foregnd_fn)
bg = cv2.imread(backgnd_fn)

img = fg + cv2.bitwise_not(bg)

plt.imshow(img)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# check to see if we should apply thresholding to preprocess the
# image
gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

plt.imshow(gray)

text = pytesseract.image_to_string(gray)
print(text)