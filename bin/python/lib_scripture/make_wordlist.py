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
# 20090204 - djd - Completed working first version. However,
#			There is a lot of potential with this process
#			but a lot of work needs to be done such as
#			CSV output on the book report files.
# 20090209 - djd - Completed optimization, works very fast
#			now. We may want to incorporate this in check_book


#############################################################
######################### Shell Class #######################
#############################################################

import codecs, os, csv
import parse_sfm

# Import supporting local classes
from encoding_manager import *
from tools import *
tools = Tools()


class MakeWordlist (object) :

	def main (self, log_manager) :

		self._log_manager = log_manager
		bookFile = log_manager._currentOutput
		log_manager._currentSubProcess = 'WordList'
		reportPath = log_manager._settings['Process']['Paths']['PATH_REPORTS']
		masterReportFileTemp = os.getcwd() + "/" + reportPath + "/wordlist-master.tmp"
		masterReportFile = os.getcwd() + "/" + reportPath + "/wordlist-master.txt"
		bookReportFileTemp = os.getcwd() + "/" + reportPath + "/" + log_manager._currentTargetID + "-wordlist.tmp"
		bookReportFile = os.getcwd() + "/" + reportPath + "/" + log_manager._currentTargetID + "-wordlist.txt"
		masterWordlist = {}
		bookWordlist = {}

# This may need to be modified if we go with the python TECKit encoding mod
# to re-encode row[0] below. Info on that mod is here:
# http://code.google.com/p/kaprao/

		# Custom processes are optional but we'll try to build them here. If we
		# can't, then we'll keep them blank and test below
		try :
			customEncodingProcess = log_manager._settings['Encoding']['Processing']['customEncodingProcess']
		except :
			customEncodingProcessMaster = ""
			customEncodingProcessBook = ""

		# If there is a custom process we will replace the file name place holders here
		customEncodingProcessMaster = customEncodingProcess.replace('[inFile]', masterReportFileTemp)
		customEncodingProcessMaster = customEncodingProcessMaster.replace('[outFile]', masterReportFile)
		customEncodingProcessBook = customEncodingProcess.replace('[inFile]', bookReportFileTemp)
		customEncodingProcessBook = customEncodingProcessBook.replace('[outFile]', bookReportFile)

		# If we already have a master word list lets look at it.
		# Also, it is assumed that this file is in the target
		# encoding so no encoding conversion will be applied
		if os.path.isfile(masterReportFile) :
			masterWordlistObject = codecs.open(masterReportFile, "r", encoding='utf-8')
			## Push it into a dictionary w/o line endings
			for line in masterWordlistObject :
				if line != "" :
					masterWordlist[line.strip()] = 1

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

		# Output the bookWordlist list to the bookWordlist
		# file, we'll overwrite the existing one and do it
		# in one shot. This needs to be done in csv.

# The csv mod doesn't handle unicode. This has more info:
# http://docs.python.org/library/csv.html#writer-objects

# Also, it would be nice if we could encode (if needed)
# row[0] which is the word we are storing. The other
# fields would not need any encoding changes

		bookWordlistObject = codecs.open(bookReportFileTemp, "w", encoding='utf-8')
		bookWordlist = handler._bookWordlist.keys()
		bookWordlist.sort()
		for f in bookWordlist :
			bookWordlistObject.write(f + " " + str(handler._bookWordlist[f]) + "\n")
		bookWordlistObject.close()


# After the book file is written out wouldn't it be better if we could open
# that up here and harvest it into a new or existing word list? If that
# were done we wouldn't need a couple of the next steps


		# Output the masterWordlist list to a temp version of
		# the masterReportFile. We will harvest this next and
		# remove duplicate words. This does not need to be csv,
		# just a simple word list. We will take the data from row[0]
# If row[0] is encoded, there would not be a need to do anything more
		masterWordlistObject = codecs.open(masterReportFileTemp, "w", encoding='utf-8')
		masterWordlist = handler._masterWordlist.keys()
		masterWordlist.sort()
		for k in masterWordlist :
			masterWordlistObject.write(k + "\n")

		masterWordlistObject.close()

		# At this point we will apply any encoding changes necessary to the
		# masterReportFile via custom post-process command on the file we
		# just wrote out. If there are none then we'll just rename our
		# temp file to the final name.

# This is not necessary if we can do a re-encode on row[0] in the book report csv file


		try :
			if tools.doCustomProcess(customEncodingProcessMaster) :
#				os.unlink(masterReportFileTemp)
				self._log_manager.log("INFO", "Custom encoding processes were run on " + bookReportFile)
				self._log_manager.log("DBUG", "Custom encoding processes command: " + customEncodingProcessMaster)
		except :
			os.rename(masterReportFileTemp, masterReportFile)
			if not customEncodingProcessMaster :
				self._log_manager.log("INFO", "No custom encoding processes were run on " + masterReportFile)
			else :
				self._log_manager.log("ERRR", "No custom encoding processes failed on " + masterReportFile + " The command was: " + customEncodingProcessMaster)

		try :
			if tools.doCustomProcess(customEncodingProcessBook) :
#				os.unlink(bookReportFileTemp)
				self._log_manager.log("INFO", "Custom encoding processes were run on " + bookReportFile)
				self._log_manager.log("DBUG", "Custom encoding processes command: " + customEncodingProcessBook)
		except :
			os.rename(bookReportFileTemp, bookReportFile)
			if not customEncodingProcessBook :
				self._log_manager.log("INFO", "No custom encoding processes were run on " + bookReportFile)
			else :
				self._log_manager.log("ERRR", "No custom encoding processes failed on " + bookReportFile + " The command was: " + customEncodingProcessBook)


class MakeWordlistHandler (parse_sfm.Handler) :
	'''This class replaces the Handler class in the parse_sfm module.'''

	def __init__(self, log_manager, bookWordlist, masterWordlist) :

		self._log_manager = log_manager
		self._bookWordlist = bookWordlist
		self._masterWordlist = masterWordlist
		self._book = ""
		self._quotemap = {}
		self._nonWordCharsMap = {}
		self._encoding_manager = EncodingManager(log_manager._settings)
		# First look for quote markers
		if log_manager._settings['General']['TextFeatures']['dumbQuotes'] == "true" :
			quoteSystem = "DumbQuotes"
		else :
			quoteSystem = "SmartQuotes"
		cList = ""
		# To prevent duplicate chars we'll put them in a mapping dictionary (nonWordCharsMap)
		# Note the use of ord() allows us to use exact unicode integer range, then we map that
		# to nothing because we want to strip those characters off of the word
		# First add quote marker characters
		for k, v, in log_manager._settings['Encoding']['Punctuation']['Quotation'][quoteSystem].iteritems() :
			# In this particular instance we want to check the len() of the string because we only
			# want single character units. However, our data coming in might not turn up that way
			# because it hasn't been decoded. For example the len of a quote mark like U+201D would
			# would be 3, not 1. By decoding we get a len of 1 for the same character.
			v = v.decode('utf_8')
			if len(v) == 1 :
				self._nonWordCharsMap[ord(v)] = None
		## Now add brackets
		for k, v, in self._log_manager._settings['Encoding']['Punctuation']['Brackets'].iteritems() :
			if k != "bracketMarkerPairs" :
				self._nonWordCharsMap[ord(v.decode('utf_8'))] = None

		# Now add word final punctuation. We use decode to be sure the comparison works right
		for k, v, in self._log_manager._settings['Encoding']['Punctuation']['WordFinal'].iteritems() :
			if v:
				self._nonWordCharsMap[ord(v.decode('utf_8'))] = None

		# This is only for report what we will be using in this
		# process for non-word characters
		for c in self._nonWordCharsMap :
			cList = cList + unichr(c) + "|"

		self._log_manager.log("INFO", "The process will exclude these characters from all words: [" + cList.rstrip('|') + "]")


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
					# Strip out any non-word chars using the mapping we made above using translate
					# Remember that translate will only work with ordinal values. It is dumb but fast
					word = word.translate(self._nonWordCharsMap)
					# Whatever is left we will add to our word dictionaries
					if word != "" :
						if self._bookWordlist.get(word) != None :
							self._bookWordlist[word] = int(self._bookWordlist.get(word)) + 1



# Why do we need two dicts here? Could we not do this in one and harvest what we
# need for the master list?


						else :
							self._bookWordlist[word] = 1
						if self._masterWordlist.get(word) != None :
							self._masterWordlist[word] = int(self._masterWordlist.get(word)) + 1
						else :
							self._masterWordlist[word] = 1

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


	def encodingConversion (self, word) :
		'''Using the TECKit module, do an encoding conversion on the
			supplied string.'''

		# Not implemented yet!

		return word

	def isWord (self, word) :
		'''Check to see if this is a word not a reference or number.'''

		if not self._encoding_manager.isReferenceNumber(word) and not self._encoding_manager.isNumber(word) :
			return True


# This starts the whole process going
def doIt (log_manager) :

	thisModule = MakeWordlist()
	return thisModule.main(log_manager)
