#!/usr/bin/python
# -*- coding: utf-8 -*-
# version: 20090120
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# Generate a word list for the current book being processed.
# This will parse the book and generate a word list and put
# it in the Reports folder.

# History:
# 20090130 - djd - Initial draft
# 20090204 - djd - Completed working first version. However,
#		There is a lot of potential with this process but
#		a lot of work needs to be done such as CSV output
#		on the book report files.
# 20090209 - djd - Completed optimization, works very fast
#		now. We may want to incorporate this in check_book
# 20090323 - djd - With Tim E's help we got the encoding
#		issues ironed out and added true CSV output.


#############################################################
######################### Shell Class #######################
#############################################################

import codecs, os, csv
import parse_sfm

# Import supporting local classes
from encoding_manager import *
from tools import *
from collections import defaultdict
tools = Tools()


class MakeBookWordlist (object) :

	def main (self, log_manager) :

		bookFile = log_manager._currentOutput
		log_manager._currentSubProcess = 'BookWordlist'
		reportPath = log_manager._settings['Process']['Paths']['PATH_REPORTS']
		bookReportFile = os.getcwd() + "/" + reportPath + "/" + log_manager._currentTargetID + "-wordlist.csv"
		bookWordlist = {}
		wordlist = []
		# Make our Report folder if it isn't there
		if not os.path.isdir(reportPath) :
			os.mkdir(reportPath)

		# Get our current book object
		bookObject = "".join(codecs.open(log_manager._currentInput, "r", encoding='utf-8'))

		# Load in the sfm parser
		parser = parse_sfm.Parser()

		# This calls a version of the handler which returns a simple
		# wordlist for us. That will be processed and information harvested
		# from it to be used in our output.
		handler = MakeWordlistHandler(log_manager, wordlist)
		parser.setHandler(handler)
		parser.parse(bookObject)

		# Now we will collect all the words from this book from the text handler
		# and we will apply any encoding changes that are necessary. The process
		# here is more complex than should be but pyTecKit doesn't allow us to
		# do multiple encodings chained together as some projects require. As such
		# we will use a home-spun module to call a shell script that will use the
		# txtconv program to do the encoding conversion externally, then bring it
		# back in to finish the processing. This is done with pipes so it seems
		# very seamless.
		# Bring in any encoding mapings we may need.
		encodingChain = log_manager._settings['Encoding']['Processing']['encodingChain']
		if encodingChain != "" :
			# Build the encoding engine(s)
			encodingChain = TxtconvChain([s.strip() for s in encodingChain.split(',')])
			# Run the conversions on all our text
			handler._wordlist = encodingChain.convert('\n'.join(handler._wordlist)).split('\n')

		# Here we create a bookWordlist dict using the defaultdict mod. Then we
		# we add the words we collected from the text handler and do the counting
		# here as well
		bookWordlist = defaultdict(int)
		for k in handler._wordlist :
			bookWordlist[k] += 1

		# Write out the new csv book word count file
		# More info on writing to csv is here:
		#	http://docs.python.org/library/csv.html#writer-objects
		cvsBookFile = csv.writer(open(bookReportFile, "wb"), dialect=csv.excel)
		cvsBookFile.writerows(bookWordlist.items())


class MakeWordlistHandler (parse_sfm.Handler) :
	'''This class replaces the Handler class in the parse_sfm module.'''

	def __init__(self, log_manager, wordlist) :

		self.log_manager = log_manager
		self._wordlist = wordlist
		self._book = ""
		self._quotemap = {}
		#self._nonWordCharsMap = {}
		self.encoding_manager = EncodingManager(log_manager._settings)
		# First look for quote markers
		#if log_manager._settings['General']['TextFeatures']['dumbQuotes'] == "true" :
			#quoteSystem = "DumbQuotes"
		#else :
			#quoteSystem = "SmartQuotes"
		cList = ""
		# To prevent duplicate chars we'll put them in a mapping dictionary (nonWordCharsMap)
		# Note the use of ord() allows us to use exact unicode integer range, then we map that
		# to nothing because we want to strip those characters off of the word
		# First add quote marker characters
		#for k, v, in log_manager._settings['Encoding']['Punctuation']['Quotation'][quoteSystem].iteritems() :
			# In this particular instance we want to check the len() of the string because we only
			# want single character units. However, our data coming in might not turn up that way
			# because it hasn't been decoded. For example the len of a quote mark like U+201D would
			# would be 3, not 1. By decoding we get a len of 1 for the same character.
			#v = v.decode('utf_8')
			#if len(v) == 1 :
				#self._nonWordCharsMap[ord(v)] = None
		## Now add brackets
		#for k, v, in self._log_manager._settings['Encoding']['Punctuation']['Brackets'].iteritems() :
			#if k != "bracketMarkerPairs" :
				#self._nonWordCharsMap[ord(v.decode('utf_8'))] = None

		# Now add word final punctuation. We use decode to be sure the comparison works right
		#for k, v, in self._log_manager._settings['Encoding']['Punctuation']['WordFinal'].iteritems() :
			#if v :
				#self._nonWordCharsMap[ord(v.decode('utf_8'))] = None

		# This is only for report what we will be using in this
		# process for non-word characters
		for c in self.encoding_manager._nonWordCharsMap :
			cList = cList + unichr(c) + "|"

		self.log_manager.log("INFO", "The process will exclude these characters from all words: [" + cList.rstrip('|') + "]")


	def start (self, tag, num, info, prefix) :
		'''This tells us when a tag starts. We will use this information to set location
			and trigger events.'''

		# Track the location
		self.log_manager.setLocation(self._book, tag, num)

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
					# Strip out any non-word chars
					word = self.encoding_manager.stripNonWordCharsFromWord(word)
					# Whatever is left we will add to our all words dictionary
					if word :
						self._wordlist.append(word)

		# This may not be needed
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

		if not self.encoding_manager.isReferenceNumber(word) and not self.encoding_manager.isNumber(word) :
			return True


# This starts the whole process going
def doIt (log_manager) :

	thisModule = MakeBookWordlist()
	return thisModule.main(log_manager)

