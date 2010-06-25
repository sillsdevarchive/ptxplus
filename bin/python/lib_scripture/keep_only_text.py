#!/usr/bin/python2.5
# -*- coding: utf_8 -*-
# version: 20090103
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# Experimental format for testing text for readability. This
# script will remove all footnotes, cross references and also
# chapter and verse number markers. All that will remain is
# the text of the book. This will give the readers the
# oportunity to read the text without all the extra-Biblical
# stuff in the way.

# History:
# 20090103 - djd - Initial draft


#############################################################
######################### Shell Class #######################
#############################################################

import codecs
import parse_sfm


class KeepOnlyText (object) :

	def main (self, log_manager) :

		bookFile = log_manager._currentOutput

		# Get our book object - Using utf_8_sig because the source
		# might be coming from outside the system and we may need
		# to be able to handle a BOM.
		bookObject = "".join(codecs.open(log_manager._currentInput, "r", encoding='utf_8_sig'))

		# Load in the parser
		parser = parse_sfm.Parser()

		# This calls a version of the handler which strips out everything
		# but the text and basic format.
		parser.setHandler(GetOnlyTextContextHandler(log_manager))
		newBookOutput = parser.transduce(bookObject)

		# Output the modified book file
		newBookObject = codecs.open(bookFile, "w", encoding='utf_8')
		newBookObject.write(newBookOutput)


class GetOnlyTextContextHandler (parse_sfm.Handler) :
	'''This class replaces the Handler class in the parse_sfm module.'''

	def __init__(self, log_manager) :

		self._log_manager = log_manager
		self._book = ""
		self._chapter = ""
		self._verse = ""
		self._lastCloseTag = ""
		self._lastCloseTagInfo = []
		self._log_manager.resetLocation()


	def start (self, tag, num, info, prefix) :
		'''This tells us when a tag starts. We will use this information to set location
			and trigger events.'''

		# Track the location
		self._log_manager.setLocation(self._book, tag, num)

		# If it's not a note we want it
		if not info.isNote :
			# If there is no number in the tag we probably want that too
			if num == "" :
				return "\\" + tag
			else :
				return ""

	def text (self, text, tag, info) :
		'''This function allows us to harvest the text from a given text element. This will
			be used to check for quotes.'''

		# Get the book id for setting our location in start()
		if tag == 'id' :
			self._book = text

		# No note text will be collected
		if not info.isNote :
			return text


	def end (self, tag, ctag, info) :
		'''This function tells us when an element is closed. We will
			use this to mark the end of events.'''

		# Is this a real closing tag?
		if tag + "*" == ctag :

			if not info.isNote :
				return "\\" + ctag


	def error (self, tag, text, msg) :
		'''Send any errors the parser finds back to the calling application.'''

		# These are paser errors that should have been dealt with in the sfm checker
		# we will ignore them here.
		# self._log_manager.log("ERRR", msg + "Marker [\\" + tag + "]")
		pass


# This starts the whole process going
def doIt (log_manager) :

	thisModule = KeepOnlyText()
	return thisModule.main(log_manager)


