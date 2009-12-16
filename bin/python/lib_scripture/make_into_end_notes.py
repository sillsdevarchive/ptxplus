#!/usr/bin/python
# -*- coding: utf-8 -*-
# version: 20090103
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# Experimental format for footnotes and cross references. The
# idea is to remove extra-Biblical matter from the text and
# allow the reader to experience the text as it was intended
# by the writer.

# This script will extract all the footnotes and cross
# reference notes in a text and move them into an external
# file which will use end-note markup to denote each note.
# This peripheral matter can then be added to the publication.

# This currently only supports a single book and will not
# overwrite an existing file. This is a limitation that will
# need to be over come in the future if this is to be used
# in a production environment.

# History:
# 20090103 - djd - Initial draft
# 20090103 - djd - More thought needs to go into the format
#		of the endnote output. Also, a way needs to be found
#		to merge endnotes from multiple books into one file.


#############################################################
######################### Shell Class #######################
#############################################################

import codecs, os
import parse_sfm


class MakeIntoEndNotes (object) :

	def main (self, log_manager) :

		self._settings = log_manager._settings
		self._preripheralPath = os.getcwd() + "/" + self._settings['Process']['Paths']['PATH_TEXTS']
		endnoteFile = self._preripheralPath + "/ENDNOTES.usfm"
		bookFile = log_manager._currentOutput

		# Get our book object
		bookObject = "".join(codecs.open(log_manager._currentInput, "r", encoding='utf-8'))

		# Load in the parser
		parser = parse_sfm.Parser()

		# This calls a version of the endnote handler which puts the notes in
		# a seperate file.
		parser.setHandler(MakeEndNoteContextHandler(log_manager))
		endnoteOutput = parser.transduce(bookObject)

		# This calls a version of the endnote handler which strips them out
		# of the main body of text.
		parser.setHandler(StripNotesContextHandler(log_manager))
		newBookOutput = parser.transduce(bookObject)

		# The whole idea of this module is to create a peripheral file
		# which contains all the notes and cross references that have
		# been stripped from this book.

		# First look for an existing endnote file and throw an error
		# if one is found. Then exit. Otherwise, create the new endnote
		# file and output the notes that were collected.
		if os.path.isfile(outputFile) :
			log_manager.log('ERRR', 'Sorry, an endnote file already exists for this project. I cannot continue.')
			return
		else :
			# Output the endnote file
			endnoteObject = codecs.open(endnoteFile, "w", encoding='utf-8')
			endnoteObject.write(endnoteOutput)
			# Output the modified book file
			newBookObject = codecs.open(bookFile, "w", encoding='utf-8')
			newBookObject.write(newBookOutput)


class MakeEndNoteContextHandler (parse_sfm.Handler) :
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

		# Return the tag we are currently, adjust for verse numbers
		if info.isNote :
			if tag == "f" or tag == "x" :
				return "\n\\p "
			else :
				if tag.find('r') > 0 :
					return "\\bd"
				elif tag.find('t') > 0 :
					return ""
				else :
					return tag


	def text (self, text, tag, info) :
		'''This function allows us to harvest the text from a given text element. This will
			be used to check for quotes.'''

		# Get the book id for setting our location in start()
		if tag == 'id' :
			self._book = text

		# Probably not much more to do here
		if info.isNote :
			if tag != "f" and tag != "x" :
				if tag.find('r') > 0 :
					return text + "\\bd*"
				else :
					return text


	def end (self, tag, ctag, info) :
		'''This function tells us when an element is closed. We will
			use this to mark the end of events.'''

		# Is this a real closing tag?
		if tag + "*" == ctag :

			# Keep track of the last closing tag and it's info
			self._lastCloseTag = ctag
			self._lastCloseTagInfo = info
			if tag != "f" and tag != "x" :
				return "\\" + ctag


	def error (self, tag, text, msg) :
		'''Send any errors the parser finds back to the calling application.'''

		# These are paser errors that should have been dealt with in the sfm checker
		# we will ignore them here.
		# self._log_manager.log("ERRR", msg + "Marker [\\" + tag + "]")
		pass


class StripNotesContextHandler (parse_sfm.Handler) :
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
			if num == "" :
				return "\\" + tag
			else :
				return "\\" + tag + " " + num

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

	thisModule = MakeIntoEndNotes()
	return thisModule.main(log_manager)
