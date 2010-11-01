#!/usr/bin/python2
# -*- coding: utf_8 -*-
# version: 20080829
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu) it may not work right
# with earlier versions.

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will insert a chapter lable (\cl) and the appropreat lable text as
# taken from the project.conf file before the first \c in a give file.

# History:
# 20080829 - djd - Initial draft
# 20081023 - djd - Refactored due to changes in project.conf
# 20081030 - djd - Added total dependence on log_manager.  This script will not
# run without it because it handles all the parameters it needs.
# 20090130 - djd - Added insert of ZWSP in cases where there is no lable insert
# text found in .conf
# 20090505 - djd - Added a filter for peripheral matter files
# 20101101 - djd - Found a really big bug with the parser.  It will need to be
# replaced in order for this script to work with files that might have sfms that
# are not recognized.


###############################################################################
############################# Initialize The Process ##########################
###############################################################################
# Firstly, import all the standard Python modules we need for this process

import codecs
import parse_sfm
# Import supporting local classes
import tools


class InsertChapterLabel (object) :


	def main(self, log_manager):

		bookFile = log_manager._currentOutput

		# Get our book object - Using utf_8_sig because the source might be
		# coming from outside the system and we may need to be able to handle a
		# BOM.
		bookObject = "".join(codecs.open(log_manager._currentInput, "r", encoding='utf_8_sig'))

		# Load in the parser
		parser = parse_sfm.Parser()

		# This calls a version of the handler which strips out everything but
		# the text and basic format.
		myHandler = InsertLableContextHandler(log_manager)
		parser.setHandler(myHandler)
		newBookOutput = parser.transduce(bookObject)

		# Output the modified book file
		newBookObject = codecs.open(bookFile, "w", encoding='utf_8')
		newBookObject.write(newBookOutput)

		if myHandler._inserted == True :
			log_manager.log('INFO', "Insert chapter lable completed successful")
		else :
			log_manager.log('ERRR', "Chapter lable insert failed on this file")


class InsertLableContextHandler (parse_sfm.Handler) :
	'''This class replaces the Handler class in the parse_sfm module.'''

	def __init__(self, log_manager) :

		self._log_manager = log_manager
		self._book = ""
		self._chapter = ""
		self._verse = ""
		self._lastCloseTag = ""
		self._lastCloseTagInfo = []
		self._log_manager.resetLocation()
		self._chapterLable = self._log_manager._settings['Format']['ChapterVerse']['cl']
		self._inserted = False


	def start (self, tag, num, info, prefix) :
		'''This tells us when a tag starts.  We will use this information to set
		location and trigger events.'''

		# Track the location
		self._log_manager.setLocation(self._book, tag, num)

		# If it's not a note we want it
		if tag == "c" :
			# If there is no number in the tag we probably want that too
			if num == "1" :
				# If there is no chapter lable we still need to insert something
				# so it will render in TeX.  We'll just put in a ZWSP (U+200B)
				if self._chapterLable == "" :
					self._log_manager.log('INFO', "Inserted chapter lable with ZWSP character (no insert text found)")
					self._inserted = True
					return "\\cl " + u'\u200B' + "\n\\" + tag + " " + num
				else :
					self._log_manager.log('INFO', "Inserted chapter lable with text: " + self._chapterLable)
					self._inserted = True
					return "\\cl " + self._chapterLable + "\n\\" + tag + " " + num
			else :
				return "\\" + tag + " " + num
		else :
			if num != "" :
				return "\\" + tag + " " + num
			else :
				return "\\" + tag


	def text (self, text, tag, info) :
		'''This function allows us to harvest the text from a given text element. This will
			be used to check for quotes.'''

		# Get the book id for setting our location in start()
		if tag == 'id' :
			self._book = text

		# No note text will be collected
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
def doIt(log_manager):

	thisModule = InsertChapterLabel()
	return thisModule.main(log_manager)
