from pdf2image import convert_from_path

def convertPDF(pdfFilePath, pdfName, outputFilePath):
	'''
	Function to pdf pages into .png images and save them in
	the given location
	:param pdfFilePath: string Input document file path
	:param pdfName: string document name (without .pdf extension)
	:param outputFilePath: string output images filepath
	'''
	pages = convert_from_path(pdfFilePath + pdfName + ".pdf", 500)

	i = 0

	for page in pages:
		outName = outputFilePath + pdfName + str(i) + ".png"
		page.save(outName, 'PNG')
		i += 1

	return(i+1)
