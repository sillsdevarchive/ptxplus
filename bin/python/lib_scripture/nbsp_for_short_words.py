#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20090120
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# Some languages have very short words that tend to fall
# at the end of sentences. If the sentence falls at the
# the end of a paragraph the word could end up on a line
# by itself. To prevent this, this process will indiscriminately
# insert a non-breaking space (U+00A0 NBSP) in front of every
# short word that falls at the end of a sentence.

# History:
# 20090120 - djd - Initial draft - Works but we may want to
#            Add some additional testing
# 20090209 - djd - Fixed a problem with not getting paragraph
#         certain kinds of paragraph covered. Also added
#        counting
# 20090911 - djd - Changed the process to work only with word
#        lengths rather than specific words.
# 20100104 - djd - Changed file encoding to utf_8_sig to prevent
#        BOM problems

#############################################################
######################### Shell Class #######################
#############################################################

import codecs
import parse_sfm

# Import supporting local classes
from encoding_manager import *
from tools import *
tools = Tools()


class NBSPForShortWords (object) :

	def main (self, log_manager) :

		bookFile = log_manager._currentOutput
		log_manager._currentSubProcess = 'NBSPForShortWords'
		replacementCount = 0
		wordLength = 0

		# Get the parameters if they exist. Note it is important to set this
		# to an integer now so it stays persistent.
		wordLength = int(tools.getModuleArguments()[0])
		log_manager.log("INFO", "Will replaced spaces with nbsp before the last word in a paragraph that has " + str(wordLength) + " characters or less.")

		# Get our book object - Using utf_8_sig because the source
		# might be coming from outside the system and we may need
		# to be able to handle a BOM.
		bookObject = "".join(codecs.open(log_manager._currentInput, "r", encoding='utf_8_sig'))

		# Load in the parser
		parser = parse_sfm.Parser()


		# This calls a version of the handler which strips out everything
		# but the text and basic format.
		handler = NBSPForShortWordsHandler(log_manager, wordLength, replacementCount)
		parser.setHandler(handler)
		newBookOutput = parser.transduce(bookObject)



		# Output the modified book file
		newBookObject = codecs.open(bookFile, "w", encoding='utf_8')
		newBookObject.write(newBookOutput)
		log_manager.log("INFO", "Replaced U+0020 with U+00A0 a total of " + str(handler._replacementCount) + " times")


class NBSPForShortWordsHandler (parse_sfm.Handler) :
	'''This class replaces the Handler class in the parse_sfm module.'''

	def __init__(self, log_manager, wordLength, count) :

		self._log_manager = log_manager
		self._book = ""
		self._encoding_manager = EncodingManager(log_manager._settings)
		self._wordLength = wordLength
		self._replacementCount = count


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

		# Find a string of text that is not an inline container
		if info.isChar or info.isPara and not info.isEnd :

			# What is the last word in this string, we want to test it
			words = text.split()

			try :
				# We only need to work with it if there are more than two words in the string
				if len(words) > 1 :
					# Grab the last word in the string
					lastWord = words[len(words)-1]
					# If it is shorter or egual to wordLength we need to join it
					if len(lastWord) <= self._wordLength :
						# Since we know what the last word is find it and replace the
						# space infront of it with a NBSP
						text = text.replace(u'\u0020' + lastWord, u'\u00A0' + lastWord)
						self._replacementCount +=1

			except :
				pass


		# Whatever happened, return the results now
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


	def cleanWord (self, word) :
		'''Do a simple clean up of the word by looking for and removing any
			punctuation found stuck to the string.'''

		return self._charTest.sub("\1", word)


# This starts the whole process going
def doIt (log_manager) :

	thisModule = NBSPForShortWords()
	return thisModule.main(log_manager)
