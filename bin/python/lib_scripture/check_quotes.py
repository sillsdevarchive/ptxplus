#!/usr/bin/python
# -*- coding: utf-8 -*-
# version: 20080729
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This class will call on the quote_manager.py sub process
# and instruct it to just check the quotes in a given file.
# This should be a very simple script.

# History:
# 20080729 - djd - Initial draft
# 20081030 - djd - Added total dependence on log_manager.
#        This script will not run without it because
#        it handles all the parameters it needs.
# 20081207 - djd - Changed the script to work independent
#        from the quote_manager but is still under
#        the check_book


#############################################################
######################### Shell Class #######################
#############################################################

import codecs
import parse_sfm
from encoding_manager import *

# Import supporting local classes
from tools import *
tools = Tools()

class CheckQuotes (object) :

	def __init__(self, log_manager) :

		self._log_manager = log_manager
		self._settings = log_manager._settings
		self._encoding_manager = EncodingManager(self._settings)
		self._currquotes = []
		self._quotation = {}
		self._brackets = {}
		self._dumbToSmartOpen = {}
		self._dumbToSmartClose = {}
		self._smartToDumb = {}
		self._openToCloseQuotes = {}
		self._closeToOpenQuotes = {}
		self._openToCloseBrackets = {}
		self._closeToOpenBrackets = {}
		self._quoteRegexp = ""
		self._newPara = False
		if self._settings['System']['TextFeatures']['contractionMarkers'] == "true" :
			self._contractionMarkers = True
		else :
			self._contractionMarkers = False

		if self._settings['System']['TextFeatures']['possessiveMarkers'] == "true" :
			self._possessiveMarkers = True
		else :
			self._possessiveMarkers = False

		self._dumbContraction = self._settings['System']['Encoding']['Punctuation']['Quotation']['DumbQuotes']['contractionMarker']
		self._smartContraction = self._settings['System']['Encoding']['Punctuation']['Quotation']['SmartQuotes']['contractionMarker']
		self._dumbPossessive = self._settings['System']['Encoding']['Punctuation']['Quotation']['DumbQuotes']['possessiveMarker']
		self._smartPossessive = self._settings['System']['Encoding']['Punctuation']['Quotation']['SmartQuotes']['possessiveMarker']
		if self._settings['System']['TextFeatures']['dumbQuotes'] == "true" :
			self._currentQuoteSystem = "DumbQuotes"
			self._contractionChar = self._dumbContraction
			self._possessiveChar = self._dumbPossessive
			self._dumbQuotes = True
		else :
			self._currentQuoteSystem = "SmartQuotes"
			self._contractionChar = self._smartContraction
			self._possessiveChar = self._smartPossessive
			self._dumbQuotes = False

		# Build a dictionary key/value pairs for quote markers used on this project
		for k, v, in self._settings['System']['Encoding']['Punctuation']['Quotation'][self._currentQuoteSystem].iteritems() :
			if v != '' :
				self._quotation[k] = v

		# Build a dictionary of key/value pairs for the brackets used on this project
		for k, v, in self._settings['System']['Encoding']['Punctuation']['Brackets'].iteritems() :
			if v != '' :
				self._brackets[k] = v

		# Build a regular expression for quote checking
		startList = ""
		endList = ""
		# First quote markers
		markers = unicode(self._quotation['quoteMarkerPairs']).split(',')
		brackets = unicode(self._brackets['bracketMarkerPairs']).split(',')
		for marker in markers :
			# We want to be sure that any elements with more than one char
			# are on the front of the list
			if len(marker) == 1 :
				endList = endList + marker.lstrip()
			else :
				startList = startList + marker.lstrip() + "|"

		# Now get our brackets
		for bracket in brackets :
			endList += "\\" + bracket.lstrip()

		self._quoteRegexp = re.compile(startList + "[" + endList + "]")

		# Build a matching lists for open to close and close to open for quotes
		for o, c in zip(markers[0::2], markers[1::2]) :
			self._openToCloseQuotes[o.lstrip()] = c.lstrip()
			self._closeToOpenQuotes[c.lstrip()] = o.lstrip()

		# Build a matching lists for open to close and close to open for brackets
		for o, c in zip(brackets[0::2], brackets[1::2]) :
			self._openToCloseBrackets[o.lstrip()] = c.lstrip()
			self._closeToOpenBrackets[c.lstrip()] = o.lstrip()

		# Build a list seperate lists for dumb and smart quotes
		dumbQuoteList = unicode(self._settings['System']['Encoding']['Punctuation']['Quotation']['DumbQuotes']['quoteMarkerPairs']).split(',')
		smartQuoteList = unicode(self._settings['System']['Encoding']['Punctuation']['Quotation']['SmartQuotes']['quoteMarkerPairs']).split(',')

		# Now build seperate lists which seperates them into close and open pair types
		for do, so, dc, sc in zip(dumbQuoteList[0::2], smartQuoteList[0::2], dumbQuoteList[1::2], smartQuoteList[1::2]) :
			self._dumbToSmartOpen[do.lstrip()] = so.lstrip()
			self._dumbToSmartClose[dc.lstrip()] = sc.lstrip()


	def processTextChunk(self, text, tag, info, lastTag, lastInfo, mode) :
		'''Main quote checking funtion which will report any errors found.'''
		res = ''
		oldMatch = None

		# Look for continued quote markes, unset the newPara switch if we are not in one
		if self._newPara :
			for i in range(len(self._currquotes) - 1 , -1 , -1) :
				if self._openToCloseBrackets.has_key(self._currquotes[i]) :
					break
				if text.find(self._currquotes[i]) == 0 :
					for j in range(i, len(self._currquotes)) :
						self._currquotes.pop()
			self._newPara = False

		# Use the regexp to find a quote marker in the chunk of text we are working with
		for match in self._quoteRegexp.finditer(text) :

			# For logging purposes, set current context from the text we are working with
			self._log_manager._currentContext = tools.getSliceOfText(text, match.start(), 10)
			if oldMatch == None and match.start() > 0:
				res = text[:match.start()]
			elif oldMatch and oldMatch.end() <= match.start() :
				res += text[oldMatch.end():match.start()]
			thisQuote = text[match.start():match.end()]
			oldMatch = match

			# Grab the character just before this one for inspection
			if match.start() > 0 :
				prechar = text[match.start() - 1]
			else :
				# Unless there is none
				prechar = ""

			# Note the last quote char we found (safely)
			try :
				lastQuote = self._currquotes[-1]
			except :
				lastQuote = ""

			# Check for contractions if they should be there, otherwise throw an error
			if self._contractionChar == thisQuote :

				# Check to see if the character just before and after the quote is word forming
				# Note: what this cannot find is a possessive marker at the end of a word. For
				# example: This is Dennis' computer. The ' on the end of the word could just
				# very well be a close quote character as a possessive marker. This may only be
				# an issue for English text.

				if match.start() > 0 \
						and self._encoding_manager.isWordForming(text[match.start()-1]) \
						and match.end() < len(text) \
						and self._encoding_manager.isWordForming(text[match.end()]) :

					if self._contractionMarkers :
						self._log_manager.log("DBUG", "Found contraction")
					else :
						self._log_manager.log("ERRR", "Quote character found in what appears to be a word.")

					# Output accordin to the mode we are in
					if mode == "swap" :
						self._log_manager.log("DBUG", "Contraction character changed from [" + thisQuote + "] to [" + self._smartContraction + "]")
						# Output a "smart" contraction marker here
						res += self._smartContraction
					else :
						# Output whatever came in
						res += thisQuote

					continue

			# Look for a close quote marker. This has the priority, we want to find them first.
			if self._closeToOpenQuotes.has_key(thisQuote) or self._closeToOpenBrackets.has_key(thisQuote) :
				# We are looking for close quote chars, reset the isOpen flag
				isOpen = False

				# Just in case we are working in dumb quote land we need to test for an open
				# quote situation which could, at first, apear to be a close quote to the logic.

				# Two opening quotes in a row (e.g. "') are allowed so we have to test here
				# for that condition in the dumb quote context
				nextIndex = match.end()
				# Move forward to the next non-open quote char
				while nextIndex < len(text) and self._openToCloseQuotes.has_key(text[nextIndex]) :
					nextIndex += 1
				# Now see if it is word forming, if so, there's a good chance this is not a close quote
				if nextIndex < len(text) and self._encoding_manager.isWordForming(text[nextIndex]) :
					# Check to see if this is a dumb open quote, if so, turn on the isOpen flag
					if self._dumbToSmartOpen.has_key(thisQuote) :
						isOpen = True
					else :
						# This is some kind of quote character but seems out of place
						self._log_manager.log("ERRR", "Quote character out of context: [" + thisQuote + "] (check for missing or misplaced spaces)")

				# If we didn't find an open quote next to a word-forming character we
				# need to examine it some more
				if not isOpen and len(self._currquotes) and \
					(self._openToCloseQuotes.get(lastQuote) == thisQuote or \
					 self._openToCloseBrackets.get(lastQuote) == thisQuote) :
					# It must be a close quote, log it, swap it, pop the stack and go on to the next char
					if self._closeToOpenQuotes.has_key(thisQuote) :
						self._log_manager.log("DBUG", "Found close quote: [" + thisQuote + "]")
					else :
						self._log_manager.log("DBUG", "Found close bracket or parenthesis: [" + thisQuote + "]")

					# Check to see if this might be the only char in the string or at the front of the
					# string. If it is, it might be misplaced and a warning should be thrown.
					# This may need some refinement as it is currently looking for a very short string
					# to test. The same condition could occur in a long string but this will miss it.
					if len(text) < 5 and match.start() == 0 and text.find('\n') > 1 :
						self._log_manager.log("WARN", "Close quote found at the end of the line, but it may be out of place, please verify. Quote found: [" + thisQuote + "]")
#                    elif text[0] == thisQuote :
					elif text[0] == thisQuote and lastInfo.isNote :
						# This might be ok if it is a bracket instead of a quote marker
						if self._closeToOpenBrackets.has_key(thisQuote) :
							self._log_manager.log("WARN", "Close bracket found right after in-line note closing marker. Context: [\\" + lastTag + "*" + thisQuote + "] (Maybe ok, please verify.)")
						else :
							self._log_manager.log("ERRR", "Close quote found right after in-line note closing marker. Context: [\\" + lastTag + "*" + thisQuote + "]")

					# Marker is swapped here if we are running in swap mode
					if mode == "swap" :
						# Check first to see that it isn't flagged as open and that it is in our range of chars
						if not isOpen and self._dumbToSmartClose.has_key(thisQuote) :
							self._log_manager.log("DBUG", "Changed quote character from [" + thisQuote + "] to [" + self._dumbToSmartClose[thisQuote] + "]")
							thisQuote = self._dumbToSmartClose[thisQuote]
					self._currquotes.pop()
					# Since we are diving out here we need to update the res string now
					res += thisQuote
					continue

				# In this situation the script is not able to find an opening quote for the
				# character found and it doesn't seem to be a closing quote either. It could
				# be a possessive marker or something else. All we can do is throw a warning
				# and move on to the next char
				elif not isOpen :
					if self._possessiveMarkers and self._possessiveChar == thisQuote :
						self._log_manager.log("WARN", "Closing character found but may be a possessive marker character. Please check: [" + thisQuote + "]")
					elif thisQuote == prechar :
						self._log_manager.log("ERRR", "Found two identical quote characters: [" + thisQuote + "]")
					else :
						self._log_manager.log("ERRR", "Closing character found but cannot match to a previous opening character: [" + thisQuote + "]")
					continue

			# Look for open quote marker
			if self._openToCloseQuotes.has_key(thisQuote) or self._openToCloseBrackets.has_key(thisQuote) :

				# The prechar should only be a space or an open bracket or nothing at all
				if prechar == '' or prechar.isspace() or self._openToCloseBrackets.has_key(prechar) :
					pass
				# But there could be an open quote in front of it but it can't be the same kind
				elif self._openToCloseQuotes.has_key(prechar) and lastQuote != thisQuote :
					pass
				else :
					# If we find a space in front of it then there probably was a typo
					if self._encoding_manager.isCharacterPunctuation(prechar) :
						self._log_manager.log("ERRR", "The preceding character to this quote marker should be a space or an open bracket the preceding character: [" + prechar + "] seems to be out of place in this context.")
					# This is probably some other kind of typo
					else :
						self._log_manager.log("ERRR", "What seems to be a non-word-forming character was found before an open quote character.")

				# Add the quote to the stack
				if self._openToCloseQuotes.has_key(thisQuote) :
					self._log_manager.log("DBUG", "Found open quote: [" + thisQuote + "]")
				else :
					self._log_manager.log("DBUG", "Found open bracket or parenthesis: [" + thisQuote + "]")

				self._currquotes.append(thisQuote)
				isOpen = False

				# Swap the quote here if running in swap mode
				if mode == "swap" :
					if self._dumbToSmartOpen.has_key(thisQuote) :
						self._log_manager.log("DBUG", "Changed quote character from [" + thisQuote + "] to [" + self._dumbToSmartOpen[thisQuote] + "]")
						thisQuote = self._dumbToSmartOpen[thisQuote]

			# Add the quote marker to the output string
			res += thisQuote

		# Append any remaining text from the previous match to the output
		if oldMatch != None and oldMatch.end() < len(text) :
			res += text[oldMatch.end():]
		elif oldMatch == None :
			res = text

		# Return the results
		return res


class QuoteContextHandler (parse_sfm.Handler) :
	'''This is the API of this module. This is called by the marker() class and enables
		it to know what to return to the calling application. Custom versions of this
		handler can be put in other applications and substitute this one. At a minimum
		the custom handler must have three functions, they are, start(), text(), and
		end().'''

	def __init__(self, log_manager, mode) :

		self._mode = mode
		self._log_manager = log_manager
		self._book = ""
		self._chapter = ""
		self._verse = ""
		self._lastTag = ""
		self._lastInfo = {}
		self._quoteChecker = CheckQuotes(self._log_manager)
		self._quoteStack = []
		self._log_manager.resetLocation()


	def start (self, tag, num, info, prefix) :
		'''This tells us when a tag starts. We will use this information to set location
			and trigger events.'''

		# Track the location
		self._log_manager.setLocation(self._book, tag, num)

		# This is where we allow for a little recursion to happen. However, we only
		# anticipate recursing one level deep into notes.
		# Here we move the quotes we found to a temp holding stack while we check
		# for quotes in the context of a note.
		if info.isNote :
			self._quoteStack.append(self._quoteChecker._currquotes)
			# Temporarily reset the main checking stack
			self._quoteChecker._currquotes = []

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

		if not info.isNonPub :
			res = self._quoteChecker.processTextChunk(text, tag, info, self._lastTag, self._lastInfo, self._mode)
		else :
			res = text

		return res


	def end (self, tag, ctag, info) :
		'''This function tells us when an element is closed. We will
			use this to mark the end of events.'''

		if info.isNote :
			# First check to see if self._quoteChcker._currquotes is
			# empty, if not we have an error
			if len(self._quoteChecker._currquotes) > 0 :
				self._log_manager.log("ERRR", "A quote was opened but not closed inside this note.")

			# Pop the stack and put the current quote back to what it
			# was before we processed the note with the popped value.
			try :
				self._quoteChecker._currquotes = self._quoteStack.pop()
			except :
				pass

		# Is this a real closing tag?
		if tag + "*" == ctag :
			return "\\" + ctag


	def error (self, tag, text, msg) :
		'''Send any errors the parser finds back to the calling application.'''

		# Any errors that are found should have been done during the sfm check
		# we will ignore them here for now.
		# self._log_manager.log("ERRR", msg + "Marker [\\" + tag + "]")
		pass


# This starts the whole process going
def doIt (log_manager):

	thisModule = CheckQuotes(log_manager)
	return thisModule

