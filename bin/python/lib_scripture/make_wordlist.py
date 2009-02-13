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

import codecs, os
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

		# Custom processes are optional
		try :
			customProcessA = log_manager._settings['General']['CustomProcesses']['customProcessA']
		except :
			customProcessA = ""

		reportPath = log_manager._settings['Process']['Paths']['PATH_REPORTS']
		masterReportFileTemp = os.getcwd() + "/" + reportPath + "/wordlist-master.tmp"
		masterReportFile = os.getcwd() + "/" + reportPath + "/wordlist-master.txt"
		bookReportFileTemp = os.getcwd() + "/" + reportPath + "/" + log_manager._currentTargetID + "-wordlist.tmp"
		bookReportFile = os.getcwd() + "/" + reportPath + "/" + log_manager._currentTargetID + "-wordlist.txt"
		masterWordlist = {}
		bookWordlist = {}

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

		# Output the bookWordlist to the bookWordlist file (we'll overwrite the existing one)
		bookWordlistObject = codecs.open(bookReportFileTemp, "w", encoding='utf-8')
		bookWordlist = handler._bookWordlist.keys()
		bookWordlist.sort()
		for f in bookWordlist :
			bookWordlistObject.write(f + " " + str(handler._bookWordlist[f]) + "\n")
		bookWordlistObject.close()

		# Output the masterWordlist to the masterReportFile (simple word list)
		masterWordlistObject = codecs.open(masterReportFileTemp, "w", encoding='utf-8')
		masterWordlist = handler._masterWordlist.keys()
		masterWordlist.sort()
		for k in masterWordlist :
			masterWordlistObject.write(k + "\n")

		masterWordlistObject.close()

		# At this point we will apply any encoding changes necessary to the
		# masterReportFile via custom post-process command on the file we
		# just wrote out.
		if customProcessA != "" :
			self.doCustomProcess(customProcessA, masterReportFileTemp, masterReportFile)
			self.doCustomProcess(customProcessA, bookReportFileTemp, bookReportFile)
			os.unlink(masterReportFileTemp)
			os.unlink(bookReportFileTemp)
		else :
			# If there were no custom processes to run then we'll just rename the .tmp
			# file to .txt so it can be identified by other processes.
			os.rename(masterReportFileTemp, masterReportFile)
			os.rename(bookReportFileTemp, bookReportFile)


	def doCustomProcess (self, process, inFile, outFile) :
		'''Run a custom process on a file.'''

		# Because we want to be able to customize the command if necessary the
		# incoming command has placeholders for the input and output. We need
		# to replace this here.
		process = process.replace('[infile]', inFile)
		process = process.replace('[outfile]', outFile)
		# But just in case we'll look for mixed case on the placeholders
		# This may not be enough but it will do for now.
		process = process.replace('[inFile]', inFile)
		process = process.replace('[outFile]', outFile)
		# Send off the command
		error = os.system(process)
		# Check to see if the copy actually took place.
		if not error :
			self._log_manager.log("INFO", "Post-process completed successfully")
		else :
			self._log_manager.log("ERROR", "Post-process did not completed successfully, command: " + process)


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
			if len(v) == 1 :
				self._nonWordCharsMap[ord(v)] = None
		## Now add brackets
		for k, v, in self._log_manager._settings['Encoding']['Punctuation']['Brackets'].iteritems() :
			if k != "bracketMarkerPairs" :
				self._nonWordCharsMap[ord(v)] = None
		# Now add word final punctuation
		for k, v, in self._log_manager._settings['Encoding']['Punctuation']['WordFinal'].iteritems() :
			if v != "" :
				self._nonWordCharsMap[ord(v)] = None

		# Report what we will be using in this process for non-word characters
		for c in self._nonWordCharsMap :
			cList = cList + chr(c) + "|"

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
					# Strip out any non-word chars using the mapping we made above
					word = word.translate(self._nonWordCharsMap)
					# Whatever is left we will add to our word dictionaries
					if word != "" :
						if self._bookWordlist.get(word) != None :
							self._bookWordlist[word] = int(self._bookWordlist.get(word)) + 1
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



		return word

	def isWord (self, word) :
		'''Check to see if this is a word not a reference or number.'''

		if not self._encoding_manager.isReferenceNumber(word) and not self._encoding_manager.isNumber(word) :
			return True


# This starts the whole process going
def doIt (log_manager) :

	thisModule = MakeWordlist()
	return thisModule.main(log_manager)
