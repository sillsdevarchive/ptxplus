#!/usr/bin/python
# -*- coding: utf-8 -*-
# version: 20080622
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This class will insert a normal USFM footnote reference
# reference in a target file.

####### Warning, this is not done yet.

# History:
# 20080623 - djd - Initial draft
# 20100104 - djd - Changed file encoding to utf_8_sig to prevent
#		BOM problems


#############################################################
#################### Initialize The Process #################
#############################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs


class InsertFootnoteRefs (object) :

	# Intitate the whole class
	def __init__(self, log_manager, inputFile):

		from markup_manager import *
		from encoding_manager import *

		settings = log_manager._settings
		self.__markup_manager = MarkupManager(settings)
		self.__encoding_manager = EncodingManager(settings)
		self.__log_manager = log_manager
		self.__inputFile = inputFile
		self.__bookID = ""
		self.__errors = 0


	def main(self):

		# Get our book object
		bookObject = codecs.open(self.__inputFile, "r", encoding='utf_8_sig')

		for line in bookObject :

			# First let's track where we are
			self.__markup_manager.setBookChapterVerse(line)
			# Get the bookID too

			# Split the line into words and look for things at the word level.
			words = line.split()

			# Keep track of what word we are on in a given line

			for word in words :

				print "Do something here"

		# Return an error code. Anything other than "0" will cause
		# our host system (Makefile) to fail.
		return self.__errors
