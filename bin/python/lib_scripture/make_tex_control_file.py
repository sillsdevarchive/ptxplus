#!/usr/bin/python
# -*- coding: utf-8 -*-
# version: 20090120
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# Generate a TeX control file for Scripture processing

# History:
# 20090209 - djd - Initial draft


#############################################################
######################### Shell Class #######################
#############################################################

import codecs, os
import parse_sfm

# Import supporting local classes
from encoding_manager import *
from tools import *
tools = Tools()


class MakeTexControlFile (object) :

	def main (self, log_manager) :

		self._log_manager = log_manager
		texControlFile = log_manager._currentOutput
		log_manager._currentSubProcess = 'MkContFile'
		sfmCount = 0

		# Look for settings to apply, not all of them will be
		# usable in every case
		try :
			oneChapOmmitRule = log_manager._settings['Format']['Scripture']['ChapterVerse']['shortBookChapterOmit']
		except :
			oneChapOmmitRule = "false"

		# Build some paths and file names
		setupFile = os.getcwd() + "/ptx2pdf-setup.txt"

		# Get our current book object
		bookObject = "".join(codecs.open(log_manager._currentInput, "r", encoding='utf-8'))

		# Load in the parser
		parser = parse_sfm.Parser()

		# This calls a version of the handler which also builds
		# our wordlist for us. Later on we will pole it to get
		# what was stored in it by the handler.
		handler = MakeTexControlFileHandler(log_manager, sfmCount)
		parser.setHandler(handler)
		parser.parse(bookObject)

		# Output the bookWordlist to the bookWordlist file (we'll overwrite the existing one)
		texControlObject = codecs.open(texControlFile, "w", encoding='utf-8')
#	echo '\\input $(TEX_PTX2PDF)' >> $$@
#	echo '\\input $(TEX_SETUP)' >> $$@
		if oneChapOmmitRule == "true" :
			texControlObject.write('\OmitChapterNumbertrue\n')
#	echo '\\ptxfile{$(PATH_TEXTS)/$(1).usfm}' >> $$@
#	echo '\\bye' >> $$@
		texControlObject.close()



class MakeTexControlFileHandler (parse_sfm.Handler) :
	'''This class replaces the Handler class in the parse_sfm module.'''

	def __init__(self, log_manager, sfmCount) :

		self._log_manager = log_manager
		self._book = ""
		self._sfmCount = sfmCount


	def start (self, tag, num, info, prefix) :
		'''This tells us when a tag starts. We will use this information to set location
			and trigger events.'''

		# Track the location
		self._log_manager.setLocation(self._book, tag, num)

		if num != "" :
			return "\\" + tag + " " + num
		else :
			return "\\" + tag


	def text (self, text, tag, info) :
		'''This function allows us to harvest the text from a given text element
			if needed.'''

		# Get the book id for setting our location in start()
		if tag == 'id' :
			self._book = text

		return text


	def end (self, tag, ctag, info) :
		'''This function tells us when an element is closed. We will
			use this to mark the end of events.'''

		# Is this a real closing tag?
		if tag + "*" == ctag :
			return "\\" + ctag


	def error (self, tag, text, msg) :
		'''Send any errors the parser finds back to the calling application.'''

		# These are paser errors that should have been dealt with in the sfm checker
		# we will ignore them here.
		# self._log_manager.log("ERRR", msg + "Marker [\\" + tag + "]")
		pass


# This starts the whole process going
def doIt (log_manager) :

	thisModule = MakeTexControlFile()
	return thisModule.main(log_manager)
