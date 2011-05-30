#!/usr/bin/env python

import sys, getopt, os
from CoreGraphics import *

def usage():
	print """usage: %s [-o output_file.pdf] file1.pdf file2.pdf
Interleave the pages of two PDF files.""" % (sys.argv[0],)

def main():
	try:
		opts, args = getopt.getopt(sys.argv[1:], "o:")
	except getopt.GetoptError:
		usage()
		sys.exit(1)
	if len(args) != 2:
		usage()
		sys.exit(1)
	file_one, file_two = args
	output_file = "%s_%s.pdf" % (os.path.splitext(file_one)[0], os.path.splitext(file_two)[0])
	for o, a in opts:
		if o == "-o":
			output_file = a

	pdf_one = CGPDFDocumentCreateWithProvider(CGDataProviderCreateWithFilename(file_one))
	pdf_two = CGPDFDocumentCreateWithProvider(CGDataProviderCreateWithFilename(file_two))
	page_count_one = pdf_one.getNumberOfPages()
	page_count_two = pdf_two.getNumberOfPages()
	rect = pdf_one.getMediaBox(1)
	c = CGPDFContextCreateWithFilename(output_file, rect)

	for page in range(1, page_count_one + 1):
		pdf_one.thisown = 0
		pdf_two.thisown = 0
		rect = pdf_one.getMediaBox(page)
		c.beginPage(rect)
		c.drawPDFDocument(rect, pdf_one, page)
		c.endPage()
		if page <= page_count_two:
			rect = pdf_two.getMediaBox(page)
			c.beginPage(rect)
			c.drawPDFDocument(rect, pdf_two, page)
			c.endPage()

	c.finish()

if __name__ == "__main__":
	main()
