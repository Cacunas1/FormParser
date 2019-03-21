from pdf2image import convert_from_path

pages = convert_from_path('Medical_License.pdf', 500)

i = 0

for page in pages:
	page.save('out'+str(i)+'.png', 'PNG')
	i = i + 1