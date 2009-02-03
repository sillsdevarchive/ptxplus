#!/usr/bin/python
# -*- coding: utf-8 -*-
# version: 20090120
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# Generate a word list for the current project. This will parse
# every file in the queue and generate a unique word list and
# put it in the Reports folder.

# History:
# 20090130 - djd - Initial draft


#############################################################
######################### Shell Class #######################
#############################################################

import codecs, os
import parse_sfm

# Import supporting local classes
from encoding_manager import *
from tools import *
tools = Tools()


class MakeWordlist (object) :

	def main (self, log_manager) :

		bookFile = log_manager._currentOutput
		reportPath = log_manager._settings['Process']['Paths']['PATH_REPORTS']
		reportFile = os.getcwd() + "/" + reportPath + "/wordlist.txt"
		wordlist = {}

		if os.path.isfile(reportFile) :
			wordlistObject = codecs.open(reportFile, "r", encoding='utf-8')
			for word in wordlistObject :
				wordlist[word.strip()] = 1

			wordlistObject.close()

		# Get our current book object
		bookObject = "".join(codecs.open(log_manager._currentInput, "r", encoding='utf-8'))

		# Load in the parser
		parser = parse_sfm.Parser()

		# This calls a version of the handler which strips out everything
		# but the text and basic format.
		handler = MakeWordlistHandler(log_manager, wordlist)
		parser.setHandler(handler)
		parser.parse(bookObject)

		# Output the wordlistObject to the wordlist file (we'll overwrite the existing one)
		newWordlistObject = codecs.open(reportFile, "w", encoding='utf-8')
		newWordlist = handler._wordlist.keys()
		newWordlist.sort()
		newWordlistObject.write("\n".join(newWordlist))
		newWordlistObject.close()


class MakeWordlistHandler (parse_sfm.Handler) :
	'''This class replaces the Handler class in the parse_sfm module.'''

	def __init__(self, log_manager, wordlist) :

		self._log_manager = log_manager
		self._wordlist = wordlist
		self._book = ""
		self._encoding_manager = EncodingManager(log_manager._settings)


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


		# Whatever happened, return the results now
		if info.isChar and not info.isNonPub :
			words = text.split()
			for word in words :
				word = word.strip()
				# Add it to the dictionary if it is a real word
				if self.isWord(word) :
					self._wordlist[word] = 1

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

	def isWord (self, word) :
		'''According to settings in the .conf file, return True if this
			proves to be a real word.'''

		return False


# This starts the whole process going
def doIt (log_manager) :

	thisModule = MakeWordlist()
	return thisModule.main(log_manager)
