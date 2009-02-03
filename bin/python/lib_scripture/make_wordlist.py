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
		masterReportFile = os.getcwd() + "/" + reportPath + "/wordlist-master.txt"
		bookReportFile = os.getcwd() + "/" + reportPath + "/" + log_manager._currentTargetID + "-wordlist.txt"
		masterWordlist = {}
		bookWordlist = {}

		# If we already have a master word list lets look at it.
		if os.path.isfile(masterReportFile) :
			masterWordlistObject = codecs.open(masterReportFile, "r", encoding='utf-8')
			# Push it into a dictionary w/o line endings
			for line in masterWordlistObject :
				data = line.split()
				masterWordlist[data[0].strip()] = data[1].strip()

			masterWordlistObject.close()

		# Get our current book object
		bookObject = "".join(codecs.open(log_manager._currentInput, "r", encoding='utf-8'))

		# Load in the parser
		parser = parse_sfm.Parser()

		# This calls a version of the handler which also builds
		# our wordlist for us. Later on we will pole it to get
		# what was stored in it by the handler.
		handler = MakeWordlistHandler(log_manager, bookWordlist, masterWordlist)
		parser.setHandler(handler)
		parser.parse(bookObject)

		# Output the bookWordlist to the bookWordlist file (we'll overwrite the existing one)
		bookWordlistObject = codecs.open(bookReportFile, "w", encoding='utf-8')
		bookWordlist = handler._bookWordlist.keys()
		bookWordlist.sort()
		for f in bookWordlist :
			bookWordlistObject.write(f + " " + str(handler._bookWordlist[f]) + "\n")
		bookWordlistObject.close()

		# Output the masterWordlist to the masterReportFile
		masterWordlistObject = codecs.open(masterReportFile, "w", encoding='utf-8')
		masterWordlist = handler._masterWordlist.keys()
		masterWordlist.sort()
		for f in masterWordlist :
			masterWordlistObject.write(f + " " + str(handler._masterWordlist[f]) + "\n")
		masterWordlistObject.close()


class MakeWordlistHandler (parse_sfm.Handler) :
	'''This class replaces the Handler class in the parse_sfm module.'''

	def __init__(self, log_manager, bookWordlist, masterWordlist) :

		self._log_manager = log_manager
		self._bookWordlist = bookWordlist
		self._masterWordlist = masterWordlist
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
					word = self.cleanWord(word)
					if word != "" :
						if self._bookWordlist.get(word) != None :
							self._bookWordlist[word] = int(self._bookWordlist.get(word)) + 1
						else :
							self._bookWordlist[word] = 1
						if self._masterWordlist.get(word) != None :
							self._masterWordlist[word] = int(self._masterWordlist.get(word)) + 1
						else :
							self._masterWordlist[word] = 1

				# How would we do a proper word count here?

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

		# First eliminate numbers and references
		if not self._encoding_manager.isReferenceNumber(word) and not self._encoding_manager.isNumber(word) :
			return True


	def cleanWord (self, word) :
		'''Do a simple clean up of the word by looking for and removing any
			punctuation found stuck to the string.'''

		# This probably needs to be optimized with a regexp or something

		# First look for quote markers
		if self._log_manager._settings['General']['TextFeatures']['dumbQuotes'] == "true" :
			quoteSystem = "DumbQuotes"
		else :
			quoteSystem = "SmartQuotes"

		for k, v, in self._log_manager._settings['Encoding']['Punctuation']['Quotation'][quoteSystem].iteritems() :
			if v != '' :
				if word.find(v) > -1 :
					word = word.replace(v, '')
		# Now look for brackets
		for k, v, in self._log_manager._settings['Encoding']['Punctuation']['Brackets'].iteritems() :
			if v != '' :
				if word.find(v) > -1 :
					word = word.replace(v, '')
		# Now look for word final punctuation
		for k, v, in self._log_manager._settings['Encoding']['Punctuation']['WordFinal'].iteritems() :
			if v != '' :
				if word.find(v) > -1 :
					word = word.replace(v, '')

		# Return whatever we got
		return word



# This starts the whole process going
def doIt (log_manager) :

	thisModule = MakeWordlist()
	return thisModule.main(log_manager)
