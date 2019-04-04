import inputFileHandling as ocr
import pdfConvert as pdf
import os

dir_path = os.getcwd()

print(dir_path)

pdf.convertPDF(
	pdfFilePath    = "E:/Users/Cristian.Acuna/Documents/POC/FormParser/input/",
	pdfName        = "Medical License",
	outputFilePath = "E:/Users/Cristian.Acuna/Documents/POC/FormParser/output/"
)

#my_text = ocr.txtExtraction(input_image="../", page=0):

#print(my_text)