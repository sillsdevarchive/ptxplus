#!/usr/bin/python
# -*- coding: utf-8 -*-
# version: 20080729
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This class will call on the parse_sfm.py to check the integrity
# of the punctuation of a given sfm file

# History:
# 20081212 - djd - Initial draft


#############################################################
######################### Shell Class #######################
#############################################################

import codecs
import parse_sfm
from encoding_manager import *

# Import supporting local classes
from tools import *
tools = Tools()


class CheckPunctuation (object) :

	def __init__(self, log_manager) :

		self._log_manager = log_manager
		self._settings = log_manager._settings
		self._encoding_manager = EncodingManager(self._settings)

		# Build a regular expression for punctuation checking
		punctChars = ""
		for k, v, in self._settings['Encoding']['Punctuation']['WordFinal'].iteritems() :
			if v != "" :
				punctChars = punctChars + v + "|"
		punctChars = '[' + punctChars.rstrip('|') + ']'
		self._punctuationRegexp = re.compile(punctChars)



	def processTextChunk(self, orgTxt, tag, info, lastCloseTag, lastCloseTagInfo) :
		'''Main quote checking funtion which will report any errors found.'''
		text = ''

		# Since we are not doing any transformations on the string in this check
		# we will look for valid exceptions and rip them out of the string before
		# further checking is done.
		for word in orgTxt.split() :
			# Over look any references
			if self._encoding_manager.isReferenceNumber(word) == False and \
				self._encoding_manager.isAbbreviation(word) == False :
				text = text + word + " "
			# Other things to check for here?

		# Take off any space we might have added
		text = text.rstrip()

		# Use the regexp to find a quote marker in the chunk of text we are working with
		for match in self._punctuationRegexp.finditer(text) :
			preChar = ""
			postChar = ""
			secondChar = ""

			# For logging purposes, set current context from the text we are working with
			self._log_manager._currentContext = tools.getSliceOfText(text, match.start(), 10)
			thisPunct = text[match.start():match.end()]

			# Grab the character just before this one for inspection
			if match.start() > 0 :
				preChar = text[match.start() - 1]
			else :
				# Unless there is none
				preChar = ""

			# Get the character just after this one for inspection
			if len(text) > match.end() :
				postChar = text[match.end()]
			else :
				postChar = ""

			# Is there word-final at the beginning of the string?
			if preChar == "" :
				# Check for an exception to this if the preceeding text was marked up with special formating
				if text[0] == thisPunct and len(text) > 1 and not lastCloseTagInfo.isFormat :
					self._log_manager.log("ERRR", "Word-final punctuation character found at the beginning of a string. Character: [" + thisPunct + "]")
				# In this case there was only one character found and it was punctuation. Proabably not good
				elif len(text) == 1 :
					self._log_manager.log("ERRR", "Lone word-final punctuation character found. Character: [" + thisPunct + "]")

			# Can't have any spaces before word-final punctuation
			if preChar == " " :
				self._log_manager.log("ERRR", "Space found before Word-final punctuation character. Character: [" + thisPunct + "]")

			# See if there is a character after the word-final punct
			if self._encoding_manager.isWordForming(postChar) :
				if tag == "v" :
					self._log_manager.log("ERRR", "Non-space character found after word-final punctuation. It was: [" + postChar + "] (check for missing or misplaced spaces)")
				else :
					self._log_manager.log("ERRR", "Non-space character found after word-final punctuation (after this verse). It was: [" + postChar + "] (check for missing or misplaced spaces)")


class PunctuationContextHandler (parse_sfm.Handler) :
	'''This class replaces the Handler class in the parse_sfm module.'''

	def __init__(self, log_manager) :

		self._log_manager = log_manager
		self._book = ""
		self._chapter = ""
		self._verse = ""
		self._punctuationChecker = CheckPunctuation(self._log_manager)
		self._lastCloseTag = ""
		self._lastCloseTagInfo = None
		self._log_manager.resetLocation()


	def start (self, tag, num, info, prefix) :
		'''This tells us when a tag starts. We will use this information to set location
			and trigger events.'''

		# Track the location
		self._log_manager.setLocation(self._book, tag, num)
#		print 'start\ttag=%s\tinfo=%r\tnum="%s"\tprefix="%s"' % (tag.ljust(8), info, num.strip(), prefix.strip())
		# Return the tag we are currently, adjust for verse numbers
		if num == "" :
			return "\\" + tag
		else :
			return "\\" + tag + " " + num


	def text (self, text, tag, info) :
		'''This function allows us to harvest the text from a given text element. This will
			be used to check for quotes.'''
#		print 'text\ttag=%s\tinfo=%r\ttext="%s"' % (tag.ljust(8) ,info, text.strip()[0:8])
		# Get the book id for setting our location in start()
		if tag == 'id' :
			self._book = text

		if not info.isNonPub :
			return self._punctuationChecker.processTextChunk(text, tag, info, self._lastCloseTag, self._lastCloseTagInfo)
		else :
			return text


	def end (self, tag, ctag, info) :
		'''This function tells us when an element is closed. We will
			use this to mark the end of events.'''
#		print 'end\ttag=%s\tinfo=%r\tctag=%s' % (tag.ljust(8), info, ctag.ljust(8))
		# Is this a real closing tag?

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

	thisModule = CheckPunctuation(log_manager)
	return thisModule
