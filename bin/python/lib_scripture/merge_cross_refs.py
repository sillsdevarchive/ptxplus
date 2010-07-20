#!/usr/bin/python2
# -*- coding: utf-8 -*-
# version: 20080729
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This methode will merge USFM cross references with footnotes
# by converting cross reference markers to footnote markers.
# When the text is rendered the cross references will merge
# in with the footnotes. This is helpful when you need to
# wrap footnotes.

# History:
# 20081226 - djd - Initial draft
# 20090831 - djd - Fixed init and log_manager bug
# 20100104 - djd - Changed file encoding to utf_8_sig to prevent
#		BOM problems


#############################################################
######################### Shell Class #######################
#############################################################

import codecs
import parse_sfm


class MergeCrossRefs (object) :

	def __init__(self, log_manager):
		self._log_manager = log_manager

	def main (self) :

		outputFile = self._log_manager._currentOutput

		# Get our book object
		bookObject = "".join(codecs.open(outputFile, "r", encoding='utf_8_sig'))

		# Load in the parser
		parser = parse_sfm.Parser()

		# This calls the cross ref merge handler which should merge the refs
		parser.setHandler(CrossRefMergeContextHandler(self._log_manager))
		output = parser.transduce(bookObject)

		# The whole idea of this module is to swap quotes but we need to be
		# sure that an output file name exists.
		if outputFile != "none" or outputFile != "" :
			outputObject = codecs.open(outputFile, "w", encoding='utf_8_sig')
			outputObject.write(output)


class CrossRefMergeContextHandler (parse_sfm.Handler) :
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

		# We are only going to work with \x family tags. This is a hard-coded
		# methode for doing this.
		if tag == "x" :
			tag = "f"
		elif tag == "xo" :
			tag = "fr"
		elif tag == "xk" :
			tag = "fk"
		elif tag == "xq" :
			tag = "fq"
		elif tag == "xdc" :
			tag = "fdc"
		elif tag == "xt" :
			tag = "ft"


		# Return the tag we are currently, adjust for verse numbers
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

		# Probably not much more to do here
		return text


	def end (self, tag, ctag, info) :
		'''This function tells us when an element is closed. We will
			use this to mark the end of events.'''

		# Is this a real closing tag?
		if tag + "*" == ctag :
			# If it is a cross ref tag we need to change it to a footnote close tag
			if tag == "x" :
				ctag = "f*"
			elif tag == "xdc" :
				ctag = "fdc*"

			# Keep track of the last closing tag and it's info
			self._lastCloseTag = ctag
			self._lastCloseTagInfo = info
			return "\\" + ctag


	def error (self, tag, text, msg) :
		'''Send any errors the parser finds back to the calling application.'''

		# These are paser errors that should have been dealt with in the sfm checker
		# we will ignore them here.
		# self._log_manager.log("ERRR", msg + "Marker [\\" + tag + "]")
		pass


# This starts the whole process going
def doIt (log_manager) :

	thisModule = MergeCrossRefs(log_manager)
	return thisModule.main()


