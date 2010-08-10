#!/usr/bin/python2
# -*- coding: utf_8 -*-
# version: 20090113
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# Some times it is necessary to "massage" the notes so they
# format better. This will insert nobreak spaces between
# references and callers and perhaps other things if needed.

# History:
# 20090113 - djd - Initial draft, seems to work but will
#            probably need more refinements and additional
#            processes added


#############################################################
######################### Shell Class #######################
#############################################################

import codecs
import parse_sfm

# Import supporting local classes
import tools


class PrepNotes (object) :

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
		parser.setHandler(PrepNotesHandler(log_manager))
		newBookOutput = parser.transduce(bookObject)

		# Output the modified book file
		newBookObject = codecs.open(bookFile, "w", encoding='utf_8')
		newBookObject.write(newBookOutput)


class PrepNotesHandler (parse_sfm.Handler) :
	'''This class replaces the Handler class in the parse_sfm module.'''

	def __init__(self, log_manager) :

		self._log_manager = log_manager
		self._book = ""


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
		'''This function allows us to harvest the text from a given text element. This will
			be used to check for quotes.'''

		# Get the book id for setting our location in start()
		if tag == 'id' :
			self._book = text

		# Grab some context for logging
		self._log_manager._currentContext = tools.getSliceOfText(text, 0, 10)

		# If it is a note we may want to make some changes
		if info.isNote :
			# Is it a reference
			if info.isRef :
				pos = 0
				newStr = ""
				for char in text :
					# Look for a normal space at the end of the string
					if pos == text.rfind(u'\u0020') :
						# Replace only that character with NBSP
						newStr = newStr + u'\u00A0'
						self._log_manager.log("INFO", "Replaced normal space with NBSP on this note reference")
					else :
						newStr = newStr + char
					pos +=1
				return newStr

			# An additional process might be to insert a NBSP or even a
			# thin space in back of the caller character to keep it with
			# the text that follows in the case of orphan callers
			else :
				return text
		else :
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

	thisModule = PrepNotes()
	return thisModule.main(log_manager)


