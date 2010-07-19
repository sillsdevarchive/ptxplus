#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20080729
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This class will call on the parse_sfm.py to check the integrity
# of a given sfm file

# History:
# 20081212 - djd - Initial draft
# 20090106 - djd - Added chapter and verse number testing.


#############################################################
######################### Shell Class #######################
#############################################################

import codecs
import parse_sfm
import sfm_definitions


class CheckSFM (object) :

	def __init__(self, log_manager) :

		self._log_manager = log_manager
		self._settings = log_manager._settings

	# Nothing is really happening here yet. This is kind of a place holder.


class SFMContextHandler (parse_sfm.Handler) :
	'''This class replaces the Handler class in the parse_sfm module.'''

	def __init__(self, log_manager) :

		self._log_manager = log_manager
		self._sfms = sfm_definitions.init_usfm()
		self._book = ""
		self._lastVerseNum = 0
		self._lastChapterNum = 0
		self._lastChar = ""
		self._nextChapterNum = 1
		self._nextVerseNum = 1
		self._lastTag = ""
		self._lastInfo = {}
		# It would be nice if we could do more about this
		self._log_manager._currentContext = "NO CONTEXT"
		self._log_manager.resetLocation()


	def start (self, tag, num, info, prefix) :
		'''This tells us when a tag starts. We will use this information to set location
			and trigger events.'''

		# Track the location
		self._log_manager.setLocation(self._book, tag, num)

		# Test for out of place markers (non-inline)
		# Check to see that we are not dealing with a BOM on the first char of the file
		if tag and prefix and prefix != u'\ufeff' :
			test = info.isInline if tag in self._sfms else False
			if not test and prefix != '\n' :
				self._log_manager.log("ERRR", "Marker \\" + tag + " did not start new line")

		# Test to see if a verse tag is following right after a chapter tag
		if tag == "v" and num == "1" and not self._lastInfo.isPara :
				self._log_manager.log("WARN", "A paragraph-type marker did not precede verse 1, found \\" + self._lastTag + " instead. Is this a problem?")

		# Test to see if there maybe a problem with the chapter number
		if tag == "c" :
			if num != "" :
				if self.numberTest(num, tag) == False :
					self._log_manager.log("ERRR", "The chapter count is off at this point, please check")
					# Try to recover for next test
					self._nextVerseNum = 1
				else :
					self._nextVerseNum = 1
				self._lastChapterNum = int(num)
			else :
				# Doubtful this would ever happen but you never know...
				self._log_manager.log("ERRR", "No number was found for this chapter tag.")

		# Test for possible verse number problems
		if tag == "v" :
			if num != "" :
				# If we find that this is a range we need to treat it different
				if num.find('-') > -1 :
					numRange = num.split('-')
					# Check for mal-formed numbers (right now we're only looking for
					# an errant "0" as the first digit)
					if numRange[0].find('0') == 0 or numRange[1].find('0') == 0 :
						self._log_manager.log("ERRR", "Found a '0' at the beginning of a number. The verse range is: " + num)
					# We will test the first number and skip over the rest
					if self.numberTest(numRange[0], tag) == False :
						self._log_manager.log("ERRR", "First verse number in range is wrong. The verse range is: " + num)
					# Take the last num in the range and add 1 to it to be ready for the next check
					self._nextVerseNum = int(numRange[1]) + 1
				else :
					if self.numberTest(num, tag) == False :
						self._log_manager.log("ERRR", "The verse count seems to be off here. Looking for verse " + str(self._lastVerseNum+1) + " but found " + num + ", please check")
						# Because of the error here we need to override the nextVerseNum setting
						self._nextVerseNum = self._lastVerseNum + 2
					# Record the last vers number
					self._lastVerseNum = int(num)
			else :
				# Doubtful this would ever happen but you never know...
				self._log_manager.log("ERRR", "No number was found for this verse tag.")

		# Test for spaces in front of inline note containers, generally that's a bad thing
		if info.isNote and info.isEnd :
			if self._lastChar == " " :
				self._log_manager.log("ERRR", "A space was found just before a note tag.")

		# Record what the last tag and info was
		self._lastTag = tag
		self._lastInfo = info

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

		# Set the lastChar for tests in start()
		self._lastChar = text[-1:]
		return text


	def end (self, tag, ctag, info) :
		'''This function tells us when an element is closed. We will
			use this to mark the end of events.'''

		# We need to test for closing of inline markers some how.
		# How will we do that? Should we set a flag earlier and
		# test here?

		# Is this a real closing tag?
		if tag + "*" == ctag :
			return "\\" + ctag


	def error (self, tag, text, msg) :
		'''Send any errors the parser finds back to the calling application.'''

		self._log_manager.log("ERRR", msg + " Marker [\\" + tag + "]")


	def numberTest (self, thisNumber, tag) :
		'''Simple test for verses and chapters to see if the given number
			what we expect it to be in the context of the given tag.'''

		# Change verse number string to integer
		thisNumber = int(thisNumber)
		match = False
		if tag == "c" :
			if thisNumber == self._nextChapterNum :
				match = True
			# Get ready for next test
			self._nextChapterNum = thisNumber + 1
		elif tag == "v" :
			if thisNumber == self._nextVerseNum :
				match = True
			# Get ready for next test
			self._nextVerseNum = thisNumber + 1
		# Return results
		return match



# This starts the whole process going
def doIt (log_manager) :

	thisModule = CheckSFM(log_manager)
	return thisModule
