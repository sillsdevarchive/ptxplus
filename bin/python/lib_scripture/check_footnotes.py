#!/usr/bin/python2.5
# -*- coding: utf_8 -*-
# version: 20080622
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This class will check footnote usage in an SFM file. It will
# follow these basic rules concerning footnotes:
#
#    There need not be a space before the opening marker
#        This helps avoid orphan callout markers
#    There need not be a space after the closing marker
#        This may be the case when a fn comes at the
#        front of a verse
#
# The focus of this script is strictly footnotes. All other
# issues will be left to other preprocessing scripts.

# History:
# 20080701 - djd - Initial draft
# 20080917 - djd - Changed output to Reports folder
# 20081023 - djd - Refactored due to changes in project.conf
# 20081030 - djd - Added total dependence on log_manager.
#        This script will not run without it because
#        it handles all the parameters it needs.
# 20081216 - djd - Changed to work with new sfm parser.
# 20090505 - djd - Added a filter for peripheral matter files
# 20100104 - djd - Changed file encoding to utf_8_sig to prevent
#        BOM problems


#############################################################
#################### Initialize The Process #################
#############################################################
# Firstly, import all the standard Python modules we need for
# this process
import sys, codecs, os

import parse_sfm
from markup_manager import *
from encoding_manager import *
from tools import *


class CheckFootnotes (object) :

	# Intitate the whole class
	def __init__(self, log_manager):

		self._settings = log_manager._settings
		self._markup_manager = MarkupManager(self._settings)
		self._encoding_manager = EncodingManager(self._settings)
		self._tools = Tools()
		self._log_manager = log_manager
		self._inputFile = log_manager._currentInput
		self._reportFilePath = self._settings['System']['Paths']['PATH_REPORTS']
		self._log_manager._currentSubProcess = 'ChkFns'


	def main (self) :

		# Set some local vars
		footnoteLines = ""

		# Get our book object - Using utf_8_sig because the source
		# might be coming from outside the system and we may need
		# to be able to handle a BOM.
		bookObject = codecs.open(self._inputFile, "r", encoding='utf_8_sig')
		footnoteListingFile = self._reportFilePath + "/" + self._tools.getScriptureFileID(self._inputFile, self._settings) + "-footnotes.txt"
		lineNumber = 0
		footnoteNumber = 0

		for line in bookObject :

			# First let's track where we are
			self._markup_manager.setBookChapterVerse(line)

			lineNumber +=1


			if self._markup_manager._footnote_tracker.hasFootnoteOpenMarkerInLine(line) == True :
				# Split the line into words and look for things at the word level.
				words = line.split()
				# Let's see what word the open marker is at
				wordCount = 0
				inFootnote = "no"
				for word in words :
					wordCount +=1
					self._log_manager._currentContext = tools.getSliceOfText(word, 1, 10)
					self._log_manager._currentLocation = "Line: " + str(lineNumber)
					# Need to compensate footnote marker check at the word-level
					if self._markup_manager._footnote_tracker.hasFootnoteOpenMarkerInLine(word + " ") == True :
						footnoteNumber +=1
						inFootnote = "yes"
						content = "\\" + self._markup_manager.getMarkerFromString(word) + " "
						# Now do a quick test on the footnote caller
						# Just so happens that wordCount is the right
						# number of words in on the line to be able to
						# grab the footnote caller character if it is
						# in the right place.
						if words[wordCount] != ("+" or "-" or "?") :
							self._log_manager.log("ERRR", "Line: " + str(lineNumber) + " The footnote caller: " + words[wordCount] + " is not valid")

						# Check to see if the \f is the first character, if it is we may have a problem.
						if word[0] == "\\" :
							self._log_manager.log("WARN", "Line: " + str(lineNumber) + " There seems to be a space before this footnote, this may not be wanted. Please verify. ")

						# Now, do we want to do more tests here?
						# We could check \fr and \ft and others
						# We'll just do this for now
					else :
						if inFootnote == "yes" :
							if self._markup_manager._footnote_tracker.hasFootnoteCloseMarker(word) == True :
								inFootnote = "no"
								content = content + word
								footnoteLines = footnoteLines + self._markup_manager.getBookChapterVerseLine() + " Line # " + str(lineNumber) + " begining at word #: " + str(wordCount) + " Contents: " + content + "\n"
								# Before we leave here let's look for some word-final
								# punctuation after the "*" and give a warning.
								if self._encoding_manager.hasClosingLastCharacter(word) == True :
									self._log_manager.log("WARN", "Line: " + str(lineNumber) + " Word-final punctuation found on the closing marker [" + word + "], please check.")

							else :
								content = content + word + " "
						else :
							continue


		# Write out footnote lines if there are any
		if footnoteLines != "" :
			# First we'll look to see if the Report folder is there
			if not os.path.isdir(self._reportFilePath) :
				os.mkdir(self._reportFilePath)

			# Now write out the file
			footnoteListingObject = codecs.open(footnoteListingFile, "w", encoding='utf_8')
			footnoteListingObject.write(footnoteLines)
			footnoteListingObject.close()

		# Report what happened
		if footnoteNumber != 0 :
			self._log_manager.log("INFO", "Checked " + str(footnoteNumber) + " footnotes. Extracted notes can be found in: " + footnoteListingFile)
		else :
			self._log_manager.log("INFO", "No footnotes found.")


# This starts the whole process going
def doIt(log_manager):

	thisModule = CheckFootnotes(log_manager)
	return thisModule.main()
