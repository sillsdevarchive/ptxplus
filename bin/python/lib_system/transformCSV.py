#!/usr/bin/python2.5
# -*- coding: utf-8 -*-
# version: 20090120
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# Do an encoding transformation on a single field in a CSV
# file and output a new version of the file. This is more
# of a utility so it doesn't interact much with other modules
# in ptxplus

# History:
# 20090406 - djd - Initial draft


#############################################################
######################### Shell Class #######################
#############################################################

import codecs, os, csv

# Import supporting local classes
from encoding_manager import *
from tools import *
tools = Tools()


class TransformCSV (object) :

	def main (self, source, target, encodingChain, field) :

		# Initialize some vars, etc.
		fieldData = ""
		orgData = []

		# Do we have a source file to work with?
		if os.path.isfile(source) :
			try :
				sourceData = csv.reader(open(source), dialect=csv.excel)

			except :
				return "Error: TransformCSV aborted, could not read source file! (File name: " + source + ")"

		else :
			return "Error: TransformCSV aborted, no source file found! (File name: " + source + ")"

		# Are our encoding mappings in place? Keep in mind that there may be switches
		# included, we'll try to filter them out assuming that they always come after
		# the file name
		for mapping in encodingChain.split(',') :
			fn = mapping.split()
			if not os.path.isfile(fn[0].strip()) :
				return "Error: TransformCSV aborted, missing mapping file: " + mapping

		# Ok, let's do some work. First we'll make a list of all the data in the field we need
		for row in sourceData :
			orgData.append(row)
			fieldData = fieldData + row[field] + "\n"

		# Initialize the encoder
		encodingChain = TxtconvChain([s.strip() for s in encodingChain.split(',')])
		# Re-encode the data
		newFieldData = encodingChain.convert(fieldData).split('\n')

		rc = 0
		cvsOutputFile = csv.writer(open(target, "w"), dialect=csv.excel)
		for row in orgData :
			row[field] = newFieldData[rc]
			rc +=1

		cvsOutputFile.writerows(orgData)



# This starts the whole process going
def doIt (source, target, processChain, field) :

	thisModule = TransformCSV()
	return thisModule.main(source, target, processChain, field)
