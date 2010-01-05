#!/usr/bin/python
# -*- coding: utf-8 -*-
# version: 20080702
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This class will check crossreference usage in an SFM file.
# It will follow these basic rules concerning crossreferences:
#
#	There need not be a space before the opening marker
#	There must be a space after the closing marker
#
# The focus of this script is strictly crossreferences. All
# other issues will be left to other preprocessing scripts.

# History:
# 20080623 - djd - Initial draft
# 20080729 - djd - Fix blank file output problem
# 20081023 - djd - Refactored due to changes in project.conf
# 20081030 - djd - Added total dependence on log_manager.
#		This script will not run without it because
#		it handles all the parameters it needs.
# 20090505 - djd - Added a filter for peripheral matter files
# 20100104 - djd - Changed file encoding to utf_8_sig to prevent
#		BOM problems


#############################################################
#################### Initialize The Process #################
#############################################################
# Firstly, import all the standard Python modules we need for
# this process
import sys, codecs
from markup_manager import *
from encoding_manager import *
from tools import *


class CheckCrossreferences (object) :

	# Intitate the whole class
	def __init__(self, log_manager):

		self._settings = log_manager._settings
		self._markup_manager = MarkupManager(self._settings)
		self._encoding_manager = EncodingManager(self._settings)
		self._tools = Tools()

		self._log_manager = log_manager
		self._inputFile = log_manager._currentInput
		self._reportFilePath = self._settings['Process']['Paths']['PATH_REPORTS']


	def main(self):

		# Set some local vars
		crossrefLines = ""

		# Filter out any peripheral files now
		if tools.isPeripheralMatter(self._inputFile) :

			return

		# Get our book object
		bookObject = codecs.open(self._inputFile, "r", encoding='utf_8_sig')
		crossrefListingFile = self._reportFilePath + "/" + self._tools.getScriptureFileID(self._inputFile, self._settings) + "-crossreferences.txt"
		lineNumber = 0
		crossRefNumber = 0

		for line in bookObject :

			# First let's track where we are
			self._markup_manager.setBookChapterVerse(line)

			lineNumber +=1


			if self._markup_manager._crossref_tracker.lookForCrossRefOpenMarker(line) == True :
				# Split the line into words and look for things at the word level.
				words = line.split()
				# Let's see what word the open marker is at
				wordCount = 0
				inCrossRef = "no"
				for word in words :
					wordCount +=1
					# Need to compensate footnote marker check at the word-level
					if self._markup_manager._crossref_tracker.lookForCrossRefOpenMarker(word + " ") == True :
						crossRefNumber +=1
						inCrossRef = "yes"
						content = "\\" + self._markup_manager.getMarkerFromString(word) + " "
						callerChar = words[wordCount]
						# Now do a quick test on the crossRef caller
						# Just so happens that wordCount is the right
						# number of words in on the line to be able to
						# grab the crossRef caller character if it is
						# in the right place.
#						print callerChar
#						if not words[wordCount] == ('+' or '-' or '?') :
						if callerChar != '-' :
							self._log_manager.logIt(self._markup_manager.getBookChapterVerse(), "ERRR", "Line: " + str(lineNumber) + " The crossRef caller: " + words[wordCount] + " is not valid")

						if callerChar != '+' :
							self._log_manager.logIt(self._markup_manager.getBookChapterVerse(), "ERRR", "Line: " + str(lineNumber) + " The crossRef caller: " + words[wordCount] + " is not valid")

						if callerChar != '?' :
							self._log_manager.logIt(self._markup_manager.getBookChapterVerse(), "ERRR", "Line: " + str(lineNumber) + " The crossRef caller: " + words[wordCount] + " is not valid")

						# Check to see if the \x is the first character, if it is we may have a problem.
						if word[0] == "\\" :
							self._log_manager.logIt(self._markup_manager.getBookChapterVerse(), "WARN", "Line: " + str(lineNumber) + " There seems to be a space before this cross ref., this may not be wanted. Please verify. ")

						# Now, do we want to do more tests here?
						# We could check \xo and \xt and others
						# We'll just do this for now
					else :
						if inCrossRef == "yes" :
							if self._markup_manager._crossref_tracker.lookForCrossRefCloseMarker(word + " ") == True :
								inCrossRef = "no"
								content = content + word
								crossrefLines = crossrefLines + self._markup_manager.getBookChapterVerse() + " Line: " + str(lineNumber) + " begining at word #: " + str(wordCount) + " Contents: " + content + "\n"
								# Before we leave here let's look for some word-final
								# punctuation after the "*" and give a warning.
								if self._encoding_manager.hasClosingLastCharacter(word) == True :
									self._log_manager.logIt(self._markup_manager.getBookChapterVerse(), "WARN", "Line: " + str(lineNumber) + " Word-final punctuation found on the closing marker [" + word + "], please check.")
							else :
								content = content + word + " "
						else :
							continue


		# Output crossreferences for inspection if there were any
		if crossrefLines != "" :
			crossrefListingObject = codecs.open(crossrefListingFile, "w", encoding='utf-8')
			crossrefListingObject.write(crossrefLines)
			crossrefListingObject.close()

		# Report what we did
		if crossRefNumber != 0 :
			self._log_manager.logIt("SYS", "INFO", "Checked " + str(crossRefNumber) + " crossreferences. Extracted references can be found in: " + crossrefListingFile)
		else :
			self._log_manager.logIt("SYS", "INFO", "No crossreferences found.")

# This starts the whole process going
def doIt(log_manager):

	thisModule = CheckCrossreferences(log_manager)
	return thisModule.main()
