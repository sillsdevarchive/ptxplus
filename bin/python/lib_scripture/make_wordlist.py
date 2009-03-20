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
import parse_sfm, teckit

# Import supporting local classes
from encoding_manager import *
from tools import *
from threading import Thread
from collections import defaultdict
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
		wordlist = []
		alreadyProcessed = False

####################
		# Load in the books meta-data file so we can check if this book
		# has been processed already. Create a new file if it isn't there
		# already. At the end of the process we'll report to it that this
		# book has been processed.
		# <Code Here>
		alreadyProcessed = True

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

		# Output the wordlist list to the bookReportFileTemp
		# file, we'll overwrite the existing one and do it
		# in one shot. This needs to be done in csv.
		# More info on writing to csv is here:
		#	http://docs.python.org/library/csv.html#writer-objects
		encodingChain = log_manager._settings['Encoding']['Processing']['encodingChain']
		encodingChain = txtconv_chain([s.strip() for s in encodingChain.split(',')])
		handler._wordlist = encodingChain.convert('\n'.join(handler._wordlist)).split('\n')

		# Here we create a word_counts dict using the defaultdict mod. Then we
		# we add the words and do the counting in the process
		word_counts = defaultdict(int)
		for k in handler._wordlist:
			word_counts[k] += 1

		# Write out the new csv book word count file
		cvs_file = csv.writer(open(bookReportFileTemp, "wb"), dialect=csv.excel)
		cvs_file.writerows(word_counts.items())

		# Load the master word list if there is one. If not, make one.
		# However, if there is one and there is an entry in the books
		# mata-data file for the book we are currently processing we
		# will not even bother opening it.
		if os.path.isfile(masterReportFile) and alreadyProcessed == False :
			masterWordlistObject = codecs.open(masterReportFile, "r", encoding='utf-8')
			## Push it into a dictionary w/o line endings

			# Use defaultdict here too!

			for line in masterWordlistObject :
				if line != "" :
					masterWordlist[line.strip()] = 1

			masterWordlistObject.close()
		else :
			# Create a new masterReportFile here and an empty dictionary
			# Use the defaultdict mod for this:
			# http://docs.python.org/library/collections.html?highlight=defaultdict#collections.defaultdict

			# Fill the new dictionary object with the book file data
			# Then write out to the master file

		# Report to the books meta-data file that this book has been processed
		# and close the file

		# <Code Here>


class MakeWordlistHandler (parse_sfm.Handler) :
	'''This class replaces the Handler class in the parse_sfm module.'''

	def __init__(self, log_manager, wordlist) :

		self._log_manager = log_manager
		self._wordlist = wordlist
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

		# Encoding handling
		# Use:
		#	converted_string = self._teckitStack.convert('some text')
		# If we want to only use part of the stack we can slice it up
		# Example:
		#	other_string = self._teckit[:-1].convert('some text')
		print log_manager._settings['Encoding']['Processing']['encodingChain']
		encodingChain = log_manager._settings['Encoding']['Processing']['encodingChain']
		encodingChain = [s.strip() for s in encodingChain.split(',')]
		print encodingChain


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
					if word:
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

		if not self._encoding_manager.isReferenceNumber(word) and not self._encoding_manager.isNumber(word) :
			return True


# This starts the whole process going
def doIt (log_manager) :

	thisModule = MakeWordlist()
	return thisModule.main(log_manager)


class txtconv_chain(list):
	"""txtconv_chain() -> empty stack
	   txtconv_chain(iterable) -> engine stack
	   iterable is a sequence of multi-txtconv conversion spec strings
		in which case an engine stack with loaded engines is returned."""

	def convert(self, data):
		"""convert the data by 'piping' it through the stack of engines."""
		args = ' '.join(['"' + tec + '"' for tec in self])
		print 'multi-txtconv.sh /dev/stdin /dev/stdout ' + args
		(cin,cout) = os.popen2('multi-txtconv.sh /dev/stdin /dev/stdout ' + args)
		def writer():
			cin.write(data); cin.flush(); cin.close()
		Thread(target=writer).start()
		try:
			result = cout.read()
			cout.close()
		except:
			print result
		return result

	@staticmethod
	def reader(f,result):
		def g():
			result[0] = f.read()
		t=Thread(target=g)
		t.start()
		return t

class teckit_stack(list):
	"""A stack of teckit engines to allow multiple sequenced conversions of
	   data when convert is called."""
	def __init__(self,iter=None):
		"""tekit_stack() -> empty stack
		   tekit_stack(iterable) -> engine stack
			  iterable can be:
				1) a sequence of teckit conversion file paths in
				   which case an engine stack with loaded engines
				   is returned.
				2) a list of tekit engines in which case they are copied
				   into the stack."""
		for i in iter:
			if type(i) == teckit.Engine:
				self.append(i)
			else:
				te = teckit.Engine(i)
				self.append(te)

	def convert(self, data):
		"""convert the data by 'piping' it through the stack of engines."""
		for te in self:
			data = te.convert(data)
		return data
