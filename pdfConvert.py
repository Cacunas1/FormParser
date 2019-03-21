from pdf2image import convert_from_path


def convertPDF(pdfFilePath, pdfName, outputFilePath):
	pages = convert_from_path(pdfFilePath + pdfName + ".pdf", 500)

	i = 0

	for page in pages:
		outName = outputFilePath + pdfName + str(i) + ".png"
		page.save(outName, 'PNG')
		i += 1