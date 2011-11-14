#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20090120
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# Do an encoding transformation on a single field in a CSV
# file and output a new version of the file. This is more
# of a utility so it doesn't interact much with many modules
# in ptxplus. Note that the TECkit transformation table
# file names must NOT have any spaces in them. It will take
# more code to facilitate spaces in file names.

# History:
# 20090406 - djd - Initial draft


#############################################################
######################### Shell Class #######################
#############################################################

import codecs, os, csv

# Import supporting local classes
from encoding_manager import *
import tools
from operator import itemgetter, setitem


class TransformCSV (object) :

	def main (self, source, target, encodingChain, field, firstRowIsHeader=True) :

		# Initialize some vars, etc.
		fieldData = ""
		orgData = []
		header = None
		encodingChain = [s.strip() for s in encodingChain.split(',')]

		# Do we have a source file to work with?
		if os.path.isfile(source) :
			try :
				orgData = list(csv.reader(open(source), dialect=csv.excel))
				if firstRowIsHeader:
					header = orgData[0]
					orgData = orgData[1:]
			except :
				return "Error: TransformCSV aborted, could not read source file! (File name: " + source + ")"

		else :
			return "Error: TransformCSV aborted, no source file found! (File name: " + source + ")"

		# Are our encoding mappings in place? Keep in mind that there may be switches
		# included, we'll try to filter them out assuming that they always come after
		# the file name
		for mapping in encodingChain :
			if not os.path.isfile(mapping.split()[0].strip()) :
				return "Error: TransformCSV aborted, missing mapping file: " + mapping

		# Ok, let's do some work. First we'll make a list of all the data in the field we need
		fields = '\n'.join(map(itemgetter(field), orgData))

		# Initialize the encoder & re-encode the data.
		convertedFields = TxtconvChain(encodingChain).convert(fields).split('\n')

		# replace the field of row with the converted value.
		map(setitem, orgData, [field]*len(orgData), convertedFields)

		cvsOutputFile = csv.writer(open(target, "w"), dialect=csv.excel)
		cvsOutputFile.writerows([header] + orgData if header else orgData)



# This starts the whole process going
# Note that the first row by default is a header. It must be explicitly
# set to false to include that data.
def doIt (source, target, processChain, field, firstRowIsHeader=True) :

	thisModule = TransformCSV()
	return thisModule.main(source, target, processChain, field, firstRowIsHeader)
