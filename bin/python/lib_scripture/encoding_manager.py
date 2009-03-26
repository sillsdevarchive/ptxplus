#!/usr/bin/python
# -*- coding: utf-8 -*-
# version: 20080619
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This class handles tracking text encoding and data at
# the word level.

# History:
# 20080704 - djd - Initial draft
# 20080801 - djd - Fixed bug in hasWordFinalLast() and
#		hasWordFinalFirst()
# 20081023 - djd - Refactored due to changes in project.conf
# 20081103 - djd - Added hasBracketOpenInLine() and
#		hasBracketCloseInLine()
# 20090324 - djd - Added the txtconv class that was written
#		by Tim Eves


#############################################################
#################### Initialize The Process #################
#############################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, re, os
from threading import Thread

# Import supporting local classes
from tools import *
tools = Tools()


class TxtconvChain(list):
	'''This will perform encoding conversions (multiple if necessary) on
		text objects passed to it. Internally it treats them like if it
		was a function, externally it is actually a piped file process.
		txtconv_chain() -> empty stack
		txtconv_chain(iterable) -> engine stack
		iterable is a sequence of multi-txtconv conversion spec strings
		in which case an engine stack with loaded engines is returned.
		Written by Tim Eves.'''

	def convert(self, data):
		"""convert the data by 'piping' it through the stack of engines.
		   data must be of type str and not type unicode."""
		args = ' '.join(['"' + tec + '"' for tec in self])
		(cin,cout) = os.popen2('multi-txtconv.sh /dev/stdin /dev/stdout ' + args)
		def writer():
			try: cin.write(data)
			finally: cin.flush(); cin.close()
		Thread(target=writer).start()
		try:
			result = cout.read()
			cout.close()
		except:
			print "Error:" + result

		return result



class EncodingManager (object) :

	'''This is the main parent class for dealing with encoding related issues.'''

	# Intitate the child classes.
	def __init__(self, settings) :

		self._settings = settings
		self._brackets = {}
		self._wordFinal = {}
		self._otherPunctuation = {}
		self._quotation = {}
		self._quotationDumb = {}
		self._quotationSmart = {}
		self._nonWordCharsMap = {}
		# Find out what kind of quote system we use
		# Define some dictionaries we'll use
		if settings['General']['TextFeatures']['dumbQuotes'] == "true" :
			self._currentQuoteSystem = "DumbQuotes"
		else :
			self._currentQuoteSystem = "SmartQuotes"

		# This is a basic Scripture number ref pattern
		# This should handle things like n:n, n:nn, nn:nn
		# or even nnn:nnn, nnn:nnn-nnn and nnn:nnn-nnn:nnn.
		# The divider could be : or .
		# The expression we use means:
		# (optional(or[)digits(:or.)digits(optional,or-digits)(optional]or))

		# Look to see if any checking needs to be done for a second
		# number encoding that could be used in xrefs and footnotes
		zero = settings['Encoding']['Numbers']['whereIsZero']
		if zero != '' and zero != ' ' :
			numRange = '[0-9' + tools.makeUnicodeNumberRange(zero) + ']+'
		else :
			numRange = '[0-9]+'

		# Build the regex for testing for references, and it works like this:
		#	(\(|\[)?	First, match on ( or [ (optional)
		#	numRange	Match on numbers 0-9 and optional second set of numbers
		#	[:.]		Match on : or .
		#	numRange	Match on numbers 0-9 and optional second set of numbers
		#	(-,' + numRange + '([:.]' + numRange + ')?)?
		#			Optional match on - or , and a number range
		#			look for an optional : or . as well followed by number range
		#	(\)|\])?	Finally, match on ] or ) (optional)
		self._basicNumRefTest = re.compile('(\(|\[)?' + numRange + '[:.]' + numRange + '(-,' + numRange + '([:.]' + numRange + ')?)?(\)|\])?')
		self._basicNumTest = re.compile( numRange )

		# Test for combined abbreviation character combinations
		# (1+ != . followed by . followed by 1+ != . followed by .)
		self._abbreviationTest = re.compile('[^.]+\.[^.]+\.')
		# Simple test to see if this is an email address
		self._emailAddressTest = re.compile('@')
		# Build a dictionary of valid bracket related key/value pairs
		for k, v, in self._settings['Encoding']['Punctuation']['Brackets'].iteritems() :
			if k != "bracketMarkerPairs" :
				if v != '' :
					self._brackets[k] = v
					# Add any relevant characters to our nonWordChars dict
					self._nonWordCharsMap[ord(v.decode('utf_8'))] = None
		# Build a dictionary of valid word-final related key/value pairs
		for k, v, in self._settings['Encoding']['Punctuation']['WordFinal'].iteritems() :
			if v != '' :
				self._wordFinal[k] = v
				# Add any relevant characters to our nonWordChars dict
				self._nonWordCharsMap[ord(v.decode('utf_8'))] = None
		# Build a dictionary of quotation related key/value pairs for whatever the specific quote system is
		for k, v, in self._settings['Encoding']['Punctuation']['Quotation'][self._currentQuoteSystem].iteritems() :
			if v != '' :
				self._quotation[k] = v
				# Add any relevant characters to our nonWordChars dict
				v = v.decode('utf_8')
				if len(v) == 1 :
					self._nonWordCharsMap[ord(v)] = None
		# Build a dictionary of quotation related key/value pairs for dumb quotes
		for k, v, in self._settings['Encoding']['Punctuation']['Quotation']['DumbQuotes'].iteritems() :
			if v != '' :
				self._quotationDumb[k] = v
		# Build a dictionary of quotation related key/value pairs for smart quotes
		for k, v, in self._settings['Encoding']['Punctuation']['Quotation']['SmartQuotes'].iteritems() :
			if v != '' :
				self._quotationSmart[k] = v
		# Build a dictionary of "other" punctuation related key/value pairs
		for k, v, in self._settings['Encoding']['Punctuation']['Other'].iteritems() :
			if v != '' :
				self._otherPunctuation[k] = v


	# General functions for looking at characters
	def hasCharacter (self, thisString, thisChar) :
		'''A simple generic check to see if a character exists in a string.'''

		if thisString.find(thisChar) != -1 :
			return True
		else :
			return False


	def hasClosingLastCharacter (self, string) :
		'''A meta-class which checks for characters which have some kind of
			compleation punctuation on the very end of the string.'''

		found = False

		# Look for sentence ending characters
		for key in self._wordFinal.keys() :
			# Get the last character in the string and compare with the value of the key
			found = self.hasCharacterEnd(string, self._wordFinal[key])

		# Look for closing quotes
		for key in self._quotation.keys() :
			# Get the last character in the string and compare with the value of the key
			found = self.hasCharacterEnd(string, self._quotation[key])

		# Look for brackets
		for key in self._brackets.keys() :
			# Get the last character in the string and compare with the value of the key
			found = self.hasCharacterEnd(string, self._brackets[key])

		return found


	def hasAnyQuoteCharacter (self, string) :
		'''A generic check for any kind of quote character in a string.'''

		found = False
		for char in string :
			# Loop through the string and look for a quote character
			if self.isAnyQuoteCharacter(char) == True :
				found = True

		return found


	def isAnyQuoteCharacter (self, char) :
		'''Check to see if a single character is a known quote character.'''

		for k, v in self._quotation.iteritems() :
			if char == v :
				print k
				return True

		return False


	def isAnyQuoteCharacterDumb (self, char) :
		'''Check to see if a single character is a known quote character.'''

		for k, v in self._quotationDumb.iteritems() :
			if char == v :
				print k
				return True

		return False


	def isAnyQuoteCharacterSmart (self, char) :
		'''Check to see if a single character is a known quote character.'''

		for k, v in self._quotationSmart.iteritems() :
			if char == v :
				return True

		return False


	def hasCharacterStart (self, word, charStart) :
		'''Generalized check to see if a word starts with a specified character.'''

		found = False
		if word[:1] == charStart :
			found = True

		return found


	def hasCharacterEnd (self, word, charEnd) :
		'''Generalized check to see if a word starts with a specified character.'''

		found = False
		if word[-1:] == charEnd :
			found = True

		return found


	def hasCharactersStartEnd (self, word, charStart, charEnd) :
		'''Generalized check to see if a word starts and ends
			with specified characters.'''

		found = False
		if word[:1] == charStart and word[-1:] == charEnd :
			found = True

		return found


	###############################################################################
	# Bracket searching functions

	def hasBracketInLine(self, line) :
		'''Take a line string and see if there are any kind of
			brackets in it.'''

		found = False
		for key in self._brackets.keys() :
			if line.find(self._brackets[key]) != -1 :
				found = True

		return found


	def hasBracketOpenInLine (self, line) :
		'''Check to see if there is any kind of open bracket in
			the line.'''

		found = False
		for key in self._brackets.keys() :
			# look for the word 'open' in the key name
			if key.find('open') != -1 :
				if line.find(self._brackets[key]) != -1 :
					found = True

		return found


	def hasBracketCloseInLine (self, line) :
		'''Check to see if there is any kind of close bracket in
			the line.'''

		found = False
		for key in self._brackets.keys() :
			# look for the word 'close' in the key name
			if key.find('close') != -1 :
				if line.find(self._brackets[key]) != -1 :
					found = True

		return found


	def hasBracketInWord (self, word) :
		'''Check if there is a bracket punctuation character
			anywhere in a word unit. This has to be a little
			smarter than hasBracketInLine.'''

		found = False
		for key in self._brackets.keys() :
			if word.find(self._brackets[key]) != -1 :
				found = True

		return found


	def hasPMarkerOpenClose (self, word) :
		'''See if there is a pair of parentheses'''

		pOpen = False
		pClose = False

		for char in word :
			if char == self._brackets['pMarker_open'] :
				pOpen = True

			if char == self._brackets['pMarker_close'] :
				pClose = True

		if pOpen == True and pClose == True :
			return True
		else :
			return False


	def hasBMarkerOpenClose (self, word) :
		'''See if there is a pair of brackets'''

		bOpen = False
		bClose = False

		for char in word :
			if char == self._brackets['bMarker_open'] :
				bOpen = True

			if char == self._brackets['bMarker_close'] :
				bClose = True

		if bOpen == True and bClose == True :
			return True
		else :
			return False


	def hasPMarkerOpen (self, word) :
		'''Check if there is an open parentheses character in the
			word/string.'''

		if word.find(self._brackets['pMarker_open']) != -1 :
			return True
		else :
			return False


	def hasBMarkerOpen (self, word) :
		'''Check if there is an open bracket character in the
			word/string.'''
		if word.find(self._brackets['bMarker_open']) != -1 :
			return True
		else :
			return False


	def hasPMarkerClose (self, word) :
		'''Check if there is an close parentheses character in the
			word/string.'''

		if word.find(self._brackets['pMarker_close']) != -1 :
			return True
		else :
			return False


	def hasBMarkerClose (self, word) :
		'''Check if there is an close bracket character in the
			word/string.'''

		if word.find(self._brackets['bMarker_close']) != -1 :
			return True
		else :
			return False


	def pMarkerOpenFirst (self, word) :
		'''See if the parentheses marker is the very first character
			in the word/string'''

		if word.find(self._brackets['pMarker_open']) == 0 :
			return True
		else :
			return False


	def bMarkerOpenFirst (self, word) :
		'''See if the bracket marker is the very first character
			in the word/string'''

		if word.find(self._brackets['bMarker_open']) == 0 :
			return True
		else :
			return False


	def pMarkerCloseLast (self, word) :
		'''See if the last character is a closing parentheses marker.'''

		if word.find(self._brackets['pMarker_close']) == len(word)-1 :
			return True
		else :
			return False


	def bMarkerCloseLast (self, word) :
		'''See if the last character is a closing bracket marker.'''

		if word.find(self._brackets['bMarker_close']) == len(word)-1 :
			return True
		else :
			return False


	###############################################################################
	# Punctuation functions

	def stripNonWordCharsFromWord(self, word) :
		'''Strip any non-word forming characters out of a word string'''

		# Strip out any non-word chars using the mapping we made above using translate
		# Remember that translate will only work with ordinal values. It is dumb but fast
		word = word.translate(self._nonWordCharsMap)

		return word


	def isWordForming (self, char) :
		'''Determine if a character is word forming by finding out what it is not.'''

		if self.isCharacterPunctuation(char) :
			return False
		elif char.isspace() :
			return False
		elif char.isdigit() :
			return False
		elif char == "" :
			return False
		return True


	def isCharacterPunctuation (self, char) :
		'''This is a simple test to see if the incoming character is
			a punctuation character or not. We will check against
			all known punctuation characters and return True if
			it is, otherwise, False.'''

		found = False
		for k, v, in self._brackets.iteritems() :
			if v == char :
				found = True
		for k, v, in self._wordFinal.iteritems() :
			if v == char :
				found = True
		for k, v, in self._quotationDumb.iteritems() :
			if v == char :
				found = True
		for k, v, in self._quotationSmart.iteritems() :
			if v == char :
				found = True
		# Something about this next set throws a Unicode error in the comparison of the 2 characters
		# We'll just comment it out for now.
		for k, v, in self._otherPunctuation.iteritems() :
			if v == char :
				found = True
		return found


	def hasWordFinalInLine (self, string) :
		'''Check to see if there is any word-final punctuation anywhere
			in a line (string with multiple words).'''

		found = False
		for key in self._wordFinal.keys() :
			if string.find(self._wordFinal[key]) > -1 :
				found = True

		return found


	def hasWordFinalInWord (self, word) :
		'''Check if there is a word-final punctuation character
			anywhere in a word unit. This has to be a little
			smarter than hasWordFinalInLine.'''

		found = False
		for key in self._wordFinal.keys() :
			if word.find(self._wordFinal[key]) > -1 :
				found = True

		return found


	def hasWordFinalFirst (self, string) :
		'''Check to see if the word-final punctuation is found on the front
			of the string.'''

		found = False
		for key in self._wordFinal.keys() :
			if self.hasCharacterStart(string, self._wordFinal[key]) == True :
#				print string
				found = True

		return found


	def hasWordFinalLast (self, word) :
		'''Check to see if there is any word-final/sentence-final punctuation
			on the very end of word string.'''

		found = False
		for key in self._wordFinal.keys() :
			if self.hasCharacterEnd(word, self._wordFinal[key]) == True :
				found = True

		return found


	def hasRepetitiveWordFinal (self, word) :
		'''Check if there are two word-final characters in a row
			caused by a typeo.'''

		found = False
		continous = 0
		for key in self._wordFinal.keys() :
#			print '[' + self._wordFinal[key] + ']+'
#			test = re.compile('[' + self._wordFinal[key] + self._wordFinal[key] + ']+')
#			test = re.compile('\.{2,}')
			# Do the test
			if len(word.split(self._wordFinal[key])) > 2 :
				for char in word :
					if char == self._wordFinal[key] :
						continous +=1
				if continous > 1 :
					found = True

		return found


	def isValidAfterWordFinal (self, word) :
		'''Check to see if the characters after a word-final punctuation
			character are valid in a word string.

			One problem we may have with this is working with strings
			that contain more than one punctuation character.'''

		puncChar = ""
		# Figure out which character we have
		for key in self._wordFinal.keys() :
			if word.find(self._wordFinal[key]) != -1 :
				puncChar = self._wordFinal[key]
				if puncChar == '' : continue
				slicedWord = word.split(puncChar)
				secondHalf = slicedWord[1]
				# Look to see if the following character is an SFM, let it go if it is.
				if secondHalf[:1] == "\\" :
					return True
				# Let's see if a closing quote character is following, that's okay too.
				# Look for both smart and dumb characters (just to make it easier)
				elif secondHalf[:1] == self._quotationDumb['qMarker1_close'] or \
					secondHalf[:1] == self._quotationDumb['qMarker2_close'] or \
					secondHalf[:1] == self._quotationDumb['qMarker3_close'] :
					return True
				elif secondHalf[:1] == self._quotationSmart['qMarker1_close'] or \
					secondHalf[:1] == self._quotationSmart['qMarker2_close'] or \
					secondHalf[:1] == self._quotationSmart['qMarker3_close'] :
					return True
				# Let's see if a closing bracket character is following, that's okay also.
				elif secondHalf[:1] == self._brackets['pMarker_close'] or \
					secondHalf[:1] == self._brackets['bMarker_close'] :
					return True
				# If none of the above are true there is probably a problem so throw a false
				else :
					return False


	def isReferenceNumber (self, word) :
		'''This will take an educated guess at if the word string sent
			to it is some kind of reference or not. This may not
			be as sophisticated needed so watch out.'''

		# This is really simple here because all the work was done
		# up in __init__ where the match was defined.
		#return self._basicNumRef.match(word)
		if self._basicNumRefTest.match(word) :
			return True
		else :
			return False


	def isNumber (self, word) :
		'''Very simple test to see if the string is a number.'''

		if self._basicNumTest.match(word) :
			return True
		else :
			return False


	def isAbbreviation (self, word) :
		'''A simple test to see if a word string is an abbreviation
			or now. If it has two or more periods in it, it
			probably is one.'''

		# Test for this has been defined in __init__
		if self._abbreviationTest.match(word) :
			return True
		else :
			return False


	def isEmailAddress (self, word) :
		'''A simple test to see if this word might be some kind of
			an email address. This is mainly for stuff found in
			periphal matter, not Scripture text. This will not
			be too complicated. We're just going to look for an
			"@" symbol and call it one if we find it.'''

		# Test for this has been defined in __init__
		# By using .search we are telling re to look
		# anywhere in the string for our @ character
		if self._emailAddressTest.search(word) :
			return True
		else :
			return False
