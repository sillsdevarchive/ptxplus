#!/usr/bin/python2.5
# -*- coding: utf_8 -*-
# version: 20080619
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This class handles tracking text markup looking and data at
# the word level. MarkupManager is the parent class which
# calls on child classes to do the work.

# History:
# 20080623 - djd - Initial draft
# 20081023 - djd - Refactored due to changes in project.conf
# 20081031 - djd - Added: hasValidClosingMarker(), hasClosingMarkerLast(),
#        and hasClosingMarker().


#############################################################
#################### Initialize The Process #################
#############################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, re


class FootnoteTracker (object) :

	'''This is a child class of the MarkupManager (below)
		for dealing footnotes within the context of
		text markup.'''

	# Intitate this class.
	def __init__(self, settings_project) :

		self._settings_project = settings_project
		self._footnoteStatus = "off"
		self._footnoteMarkers = {}
		# Build a dictionary of valid footnote related key/value pairs
		for k, v, in self._settings_project['System']['Markup']['Footnotes'].iteritems() :
			self._footnoteMarkers[k] = v


	def footnoteStatus (self) :

		return "footnoteStatus() - Not written yet"


	def hasFootnoteOpenMarkerInLine (self, line) :
		'''Return True or False as to if a proper footnote open
			marker exists in the line given. This will
			return False if you are checking at the word
			level because it has to have a space following
			the marker to be valid. Use hasFootnoteOpenMarker()
			when doing word-level checks.'''

		if line.find("\\" + self._footnoteMarkers['footnoteOpenMarker'] + " ") >= 0 :
			return True
		else :
			return False


	def hasFootnoteOpenMarker (self, word) :
		'''Return True or False as to if a footnote open marker
			marker exists in the word given. This may not give
			accurate results when checking at the line level
			where spaces are found. A valid open marker must
			have a space following it. Use hasFootnoteOpenMarkerInLine()
			when doing line-level checks.

			At the word level a valid footnote open marker
			must be at the end of the string. That's where
			we will look. If it is there but it is not well
			formed we will still return False.'''

		marker = "\\" + self._footnoteMarkers['footnoteOpenMarker']
		markerLength = len(marker)
		# Note: The "-" in front of markerLength gives me the characters
		# at the end of the string by the length of markerLength.
		markerSlice = word[-markerLength:]
		if markerSlice == marker :
			return True
		else :
			return False


	def hasFootnoteCloseMarker (self, string) :
		'''Return True or False as to if a proper footnote close
			marker exists in the string given.'''

		if string.find("\\" + self._footnoteMarkers['footnoteCloseMarker']) >= 0 :
			return True
		else :
			return False



class CrossReferenceTracker (object) :

	#'''This is a child class for dealing cross references within the
	#context of text markup.'''

	# Intitate this class.
	def __init__(self, settings_project) :

		self._settings_project = settings_project
		self._crossReferenceStatus = "off"
		self._crossRefMarkers = {}
		for k, v, in self._settings_project['System']['Markup']['CrossRefereces'].iteritems() :
			self._crossRefMarkers[k] = v


	def lookForCrossRefOpenMarker (self, string) :
		'''Return True or False as to if a proper crossRef open
			marker exists in the string given. This will
			return False if you are checking at the word
			level because it has to have a space following
			the marker to be valid. That must be compensated
			for when doing word-level checks.'''

		if string.find("\\" + self._crossRefMarkers['crossRefOpenMarker'] + " ") > 0 :
			return True
		else :
			return False


	def lookForCrossRefCloseMarker (self, string) :
		'''Return True or False as to if a proper crossRef close
			marker exists in the string given.'''

		if string.find("\\" + self._crossRefMarkers['crossRefCloseMarker']) > 0 :
			return True
		else :
			return False



#class ParagraphTracker (object) :

	#'''This is a child class for tracking paragraph level data
	#within the context of text markup.'''

	## Intitate this class.
	#def __init__(self) :


#class MetaDataTracker (object) :

	#'''This is a child class for tracking meta-data within the
	#context of text markup. It will include things like chapter
	#and verse locations, book IDs and more.'''

	## Intitate this class.
	#def __init__(self) :


class MarkupManager (object) :

	'''This is the main parent class for dealing with text
		markup. It will support the following child
		classes that are defined above.'''

	# Intitate the child classes.
	def __init__(self, settings_project) :

		# Initialize some sub-classes
		self._footnote_tracker = FootnoteTracker(settings_project)
		self._crossref_tracker = CrossReferenceTracker(settings_project)
		#footnote_tracker = FootnoteTracker(settings_project)
		#cross_reference_tracker = CrossReferenceTracker(settings_project)
		# Intialize class specific stuff
		self._settings_project = settings_project
		self._fileIdentification = ""
		self._sectionHeading = ""
		self._chapterNumber = 0
		self._verseNumber = 0
		self._lineNumber = 0
		self._wordNumber = 0
		self._characterNumber = 0
		self._allUSFM = []
		self._allParagraph = []
		# Initialize varables from the project settings file.
		# Pushing the dynamic vars in __dict__ allows them to be persistant.
		# However, we might want to look at using a regular dictionary object
		# to do this same thing. It is a bit dodgy using __dict__.
		for k, v, in self._settings_project['System']['Markup']['Identification'].iteritems() :
			self.__dict__[k] = v
		for k, v, in self._settings_project['System']['Markup']['ChaptersVerses'].iteritems() :
			self.__dict__[k] = v
		for k, v, in self._settings_project['System']['Markup']['USFMAllMarkers'].iteritems() :
			self._allUSFM += v

		# As these are already in list form we will take them like this
		self._allParagraph = self._settings_project['System']['Markup']['USFMAllMarkers']['paragraphs']


	def setLocation (self, word, char) :
		'''This is an advanced location tracker that will be used by
			some routines that use this class. It will keep track
			of book ID, chapter, verse, line, word, and character.'''

		self._wordNumber = word
		self._characterNumber = char


	def setBookChapterVerse (self, line) :
		'''This is a basic location tracker that will be used by
			all routines that use this class. It is limited
			to tracking book ID, chapter and verse.'''

		# We'll track lines automatically with this too
		self._lineNumber +=1

		# Now look at things at the word level
		wordsInLine = line.split()
		# This prevents blank lines from giving us a problem
		if len(wordsInLine) > 0 :
			# Get the Book ID if its there
# Debug point        print line
			if wordsInLine[0] == "\\" + self.__dict__['fileIdentification'] :
				self._fileIdentification = wordsInLine[1]
				# Set the chapter number back to 0 (just in case)
				self._chapterNumber = 0
			# While we are at it we could look for and get the chapter and verse ref too.
			elif wordsInLine[0] == "\\" + self.__dict__['chapterNumber'] :
				# Now update the chapter location
				self._chapterNumber = wordsInLine[1]
				# Set the verse number back to 0
				self._verseNumber = 0
			elif wordsInLine[0] == "\\" + self.__dict__['verseNumber'] :
				self._verseNumber = wordsInLine[1]


	def getBookID (self) :
		'''Return whatever book ID is present in the class.'''

		return self._fileIdentification


	def getChapterNumber (self) :
		'''Return the number of chapter we're in.'''

		return self._chapterNumber


	def getVerseNumber (self) :
		'''Return the number of the verse we're in.'''

		return self._verseNumber


	def getLineNumber (self) :
		'''Return the current line number we are on as set by
			setBookChapterVerse().'''

		return self._lineNumber


	def getWordNumber (self) :
		'''Return the number of the word in a line as tracked by
			setLocation().'''

		return self._wordNumber


	def getCharacterNumber (self) :
		'''Return the number of the character we are on in a word
			as tracked by setLocation().'''

		return self._characterNumber


	def getBookChapterVerse (self) :
		'''Return a simple string of Book:Chapter:Verse.'''

		return self._fileIdentification + " " + str(self._chapterNumber) + ":" + str(self._verseNumber)


	def getBookChapterVerseLine (self) :
		'''Return a simple formated string that has the Book, Chapter, Verse and Line Number.'''

		# Line number seems to be the most helpful info when tracking down errors, we'll put that first
		string = "Line: " + str(self._lineNumber) + " (" + self._fileIdentification + ":" + str(self._chapterNumber) + ":" + str(self._verseNumber) + ")"
		return string


	def getExactLocation (self) :
		'''Return a simple formated string that has the exact location of where we are at
			in a given text. The string will be formated as follows:
				At: l:w:c (b:c:v)'''

		# Line number seems to be the most helpful info when tracking down errors, we'll put that first
		return str(self._lineNumber) + ":" + str(self._wordNumber) + ":" + str(self._characterNumber)


	def getMarkerFromString (self, string) :
		'''This will extract an SFM marker from a string. It does not
			bother to figure out if it is a valid one or not and
			if there are more than one in the string it will only
			work with the first one.'''

		subStr = string.split("\\")
		if len(subStr) > 1 :
			if subStr[1].find("*") > 0 :
				# This looks really dumb but it works so far
				found = subStr[1]
				m = found.split("*")
				marker = str(m[0]) + "*"
			else :
				marker = subStr[1]
		else :
			if subStr[0].find("*") > 0 :
				# This looks really dumb but it works so far
				found = subStr[0]
				m = found.split("*")
				marker = str(m[0]) + "*"
			else :
				marker = subStr[0]

		return marker


	def isValidMarkup (self, string) :
		'''This will test to see if the string passed to it is a valid USFM
			marker. It will return either True or False.'''

		thisMarker = self.getMarkerFromString(string)
		for marker in self._allUSFM :
			if thisMarker == marker :
				return True

		return False


	def isValidParagraphMarker (self, string) :
		'''Test to see if this is a valid paragraph marker.'''

		found = False
		thisMarker = self.getMarkerFromString(string)
		for marker in self._allParagraph :
			if thisMarker == marker :
				return True

		return False


	def isValidInLineMarker (self, string) :
		'''Test to see if the marker handed to it is a valid in-line
			marker or not.'''

		inline = False
		thisMarker = self.getMarkerFromString(string)
		# Check if this is a closing marker or not. If not we
		# will pretend it is and check to see if it is valid
		# in the context of an inline marker.
		if thisMarker[-1:] == "*" :
			if self.isValidMarkup(thisMarker) == True :
				inline = True
		else :
			if self.isValidMarkup(thisMarker + '*') == True :
				inline = True

		return inline


	def hasLineParagraphMarkerFirst (self, line) :
		'''Check to see if the first "word" in a line is a
			valid paragraph marker.'''

		words = line.split()
		# Just in case there is a blank line we will use some
		# exception handling here
		try :
			if self.isValidParagraphMarker(words[0]) == True :
				return True
			else :
				return False
		except :
			return False


	def hasOpeningMarker (self, string) :
		'''See if there is something that could be a well-formed
			closing marker any place in the string.'''

		# Build the rexep, it works something like this:
		#    ^.*\\        = Group(0) - Match any characters on the front of the string up to a \
		#    ([\w]+)        = Group(1) - Match any number of characters (normally 1-4 characters)
		#    [^/]*$        = Group(2) - Ignore everything to the end of the string
		test = re.compile('^.*\\\\([\w]+)[^/]*$')

		# Do the test
		if test.match(string) == None :
			return False
		else :
			return True


	def hasValidOpeningMarker (self, string) :
		'''You suspect that a opening marker exists in a given string.
			This will varify that a marker exists and it is valid.
			Then it will return True, if not, then False.'''

		# Is there even a opening marker?
		if self.hasOpeningMarker(string) == True :
			# Is it valid?
			if self.isValidMarkup(string) == True :
				return True
		else :
			return  False


	def hasOpeningMarkerLast (self, string) :
		'''Check a string to see if it has an opening USFM at
			the very end of it.'''

		# First test to see if it even has one
		if self.hasValidOpeningMarker(string) == True :
			# Now see if it is at the end of the string
			# Build the rexep, it works something like this:
			#    ^.*\\        = Match any characters on the front of the string up to a \
			#    [\w]+        = Match any number of characters (normally 1-4 characters)
			#    $        = Nothing should follow
			test = re.compile('^.*\\\\[\w]+$')
			# Do the test
			if test.match(string) == None :
				return False
			else :
				return True

		else :
			return False


	def hasClosingMarker (self, string) :
		'''See if there is something that could be a well-formed
			closing marker any place in the string.'''

		# Build the rexep, it works something like this:
		#    ^.*\\        = Group(0) - Match any characters on the front of the string up to a \
		#    ([\w]+)        = Group(1) - Match any number of characters (normally 1-4 characters)
		#    ([*])        = Group(2) - Match and asterisk only
		#    [^/]*$        = Group(3) - Ignore everything to the end of the string
		test = re.compile('^.*\\\\([\w]+)([*])[^/]*$')

		# Do the test
		if test.match(string) == None :
			return False
		else :
			return True


	def hasValidClosingMarker (self, string) :
		'''You suspect that a closing marker exists in a given string.
			This will varify that a marker exists and it is valid.
			Then it will return True, if not, then False.'''

		# Is there even a closing marker?
		if self.hasClosingMarker(string) == True :
			# Is it valid?
			if self.isValidMarkup(string) == True :
				return True
		else :
			return  False


	def hasClosingMarkerLast (self, string) :
		'''Look to see if something that could be a closing marker
			is parked at the end of this string Return True if so.
			This is different from lookForWordFinalMarkup() as it
			is looking specificly for a closing markers.'''

		# First test to see if it even has one
		if self.hasValidClosingMarker(string) == True :
			# Now see if it is at the end of the string
			# Build the rexep, it works something like this:
			#    ^.*\\        = Match any characters on the front of the string up to a \
			#    [\w]+        = Match any number of characters (normally 1-4 characters)
			#    [*]        = Match and asterisk only
			#    $        = Nothing should follow
			test = re.compile('^.*\\\\[\w]+[*]$')
			# Do the test
			if test.match(string) == None :
				return False
			else :
				return True

		else :
			return False


	def lookForDoubleMarkup (self, string) :
		'''There should never be two SFM markers in the same string. This
			test will return True if it finds two or more.'''

		if string.count("\\") > 1 :
			return True
		else :
			return False


	def lookForWordInitialMarkup (self, string) :
		'''This is a general search routine for markup at the begining of
			a string. This could be a bad thing so we should do some
			further tests when one is found to validate the marker
			This will return only True or False depending on if it
			finds a "\" at the begining of the string.'''

		if string.find("\\") == 0 :
			return True
		else :
			return False


	def lookForWordMedialMarkup (self, string) :
		'''This is a general search routine for markup near the middle of
			a string. What this means is that something that is not
			markup must come before and after a valid USFM sequence
			This will return True if markup is found in the middle.'''

		if string.find("\\") > 0 :
			lookAt = string.split("\\")
			for marker in self._allUSFM :
				if lookAt[1].find(marker) == 0 :
					found = marker

			if len(lookAt[1]) >= len(marker) :
				return True
		return False


	def lookForWordFinalMarkup (self, string) :
		'''This is a general search routine for markup at the end of a
			string. This is generally where it will be found. Unlike
			hasClosingMarkerLast(), this is designed to find any kind
			of marker. It will return only True or False'''

		# Build the rexep, it works something like this:
		#    ^.*\\        = Group(0) - Match any characters on the front of the string up to a \
		#    ([\w]+)        = Group(1) - Match any number of characters (normally 1-4 characters)
		#    ([*])        = Group(2) - Match and asterisk only
		#    [^/]*$        = Group(3) - Ignore everything to the end of the string
		test = re.compile('^.*\\\\[\w]+([*]?)$')

		# Do the test
		if test.match(string) == None :
			return False
		else :
			return True


	def identifyMarkup (self) :
		'''This will look for markup in a string and return the usfm
			marker name of the marker found, or it will return None.'''

		return "identifyMarkup() - Not written yet"


	def extractBookID (self, inputFile) :
		'''Only find the book ID in an USFM file. This is for special
			one-off kind of processes.'''

		# Get our book object - Using utf_8_sig because the source
		# might be coming from outside the system and we may need
		# to be able to handle a BOM.
		bookObject = codecs.open(inputFile, "r", encoding='utf_8_sig')

		for line in bookObject :

			# First let's track where we are
			self.setBookChapterVerse(line)

			if self._fileIdentification != "" :
				# When we find it we'll stop and return it
				return self._fileIdentification

		# Otherwise we return nothing at all.
		return None


	def checkSFMInventory (self, sfm) :
		'''This will check to see if an SFM code exsits in the
			SFM inventory section of the project.ini file.'''

		# Not written yet.
		return False


	def addToSFMInventory (self, sfm) :
		'''This will add an SFM marker to the SFM inventory section
			of the project.ini file.'''

		# Not written yet
		return False
