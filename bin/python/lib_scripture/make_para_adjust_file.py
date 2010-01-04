#!/usr/bin/python
# -*- coding: utf-8 -*-
# version: 20080622
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This will create a paragraph adjustment file that the ptx2pdf
# XeTeX macros use to stretch or shrink paragraphs that are
# specified by c/v location.

# This script assumes the text coming at it is Unicode and
# is marked up with valid USFM. Also, at this time, it cannot
# deal with verses that are broken by line breaks. Perhaps
# at some point it will but for now, all lines need to begin
# with a valid USFM marker.

# History:
# 20080331 - djd - Added check for \f in loc var. This may
#		need to be expanded to cover other problems
#		that arise.
# 20080403 - djd - Split the configuration vars into two files
#		for better management of vars.
# 20080403 - djd - added parameter in the config_proj file
#		for setting the length of paragraphs we count.
# 20080429 - djd - eliminated config_proj and config_gen,
#		condensed to just config to simplify
# 20080601 - djd - Changed this script to work as a class so
#		it can be called and logged easier.
# 20080626 - djd - Reworked to be called by the process_
#		scripture_text.py and newer logging system.
# 20081023 - djd - Refactored due to changes in project.conf
# 20081030 - djd - Added total dependence on log_manager.
#		This script will not run without it because
#		it handles all the parameters it needs.
# 20081230 - djd - Changed over to work stand-alone instead
#		of through version control.
# 20090504 - djd - Added a filter for peripheral matter files


#############################################################
#################### Initialize The Process #################
#############################################################
# Firstly, import all the standard Python modules we need for
# this process

import sys, codecs, os
from markup_manager import *

# Import supporting local classes
from tools import *
tools = Tools()


class MakeParaAdjustFile (object) :

	# Intitate the whole class
	def __init__(self, log_manager) :

		self._settings = log_manager._settings
		self._markup_manager = MarkupManager(self._settings)
		self._log_manager = log_manager
		self._inputFile = log_manager._currentInput
		self._outputFile = self._inputFile + ".adj"
		self._bookID = log_manager._currentTargetID
		self._adjustLinesWritten = 0
		self._poetryMarkers = {}
		for k, v, in self._settings['Markup']['Poetry'].iteritems() :
			self._poetryMarkers[k] = v
		self._paragraphMarkers = {}
		for k, v, in self._settings['Markup']['Paragraphs'].iteritems() :
			self._paragraphMarkers[k] = v


	def writeAdjLine (self, verseCount, footnoteCount, wordCount, \
		location, paragraphType, paragraphLegnth, outputObject) :
		'''Write out adjustment line to the adjustment file.'''

		if wordCount > paragraphLegnth :
			# Don't write if there is no location value
			if location != "" :
				outputObject.write(location + "    % " \
					+ "v=" + str(verseCount) \
					+ " f=" + str(footnoteCount) \
					+ " w=" + str(wordCount) \
					+ " t=" + paragraphType + "\n")

				self._adjustLinesWritten +=1


	def main(self):

# This needs to be rewritten to use the sfm parser which would simplify it somewhat


		# Pull in any settings that we need from the project INI file
		# You may need to use int() to be sure numbers work right
		adjustParaLength = int(self._settings['TeX']['AdjustParagraph']['adjustParaLength'])
		verseNumberMarker = "\\" + self._settings['Markup']['ChaptersVerses']['verseNumber']
		footnoteOpenMarker = "\\" + self._settings['Markup']['Footnotes']['footnoteOpenMarker']

		if os.path.isfile(self._outputFile) :
			# If it exists that may be a problem as we don't want to
			# accidently wipe out any adjustment data that has been
			# entered by the user. For this reason. we will not complete
			# the process if we find one. We'll just output a warning
			# to the log and exit gracefully.

			self._log_manager.log("INFO", "The file " + self._outputFile + " already exists so I will not build a new one.")

			return

		if tools.isPeripheralMatter(self._inputFile) :
			# If the parent file belongs to the peripheral mater we will
			# not go through with the process

			self._log_manager.log("INFO", "The " + self._inputFile + " is part of the peripheral mater so the process is being halted.")

			return

		# Otherwise we'll just continue on by opening up a new .adj file
		outputObject = codecs.open(self._outputFile, "w", encoding='utf_8_sig')

		# Open up our book file (Unicode encoded)  and suck in the
		# entire body of text.
		inputObject = codecs.open(self._inputFile, "r", encoding='utf_8_sig')

		paragraph = "off"
		verseCount = 0
		footnoteCount = 0
		wordCount = 0
		paragraphType = ""
		locationLine=""

		for line in inputObject :
			# First let's keep track of where we are in the book
			self._markup_manager.setBookChapterVerse(line)

			# Look for paragraph elements
			wordsInLine = line.split()

			# Count the words in this line
			if paragraph == "on" :
				if len(wordsInLine) > 0 :
					# Look to see if this is a verse line
					if wordsInLine[0] == verseNumberMarker :
						if verseCount == 0 :

							# The output needs a special format so we need to get each component.
							self._bookID = self._markup_manager.getBookID()
							chapter = str(self._markup_manager.getChapterNumber())
							verse = str(self._markup_manager.getVerseNumber())

							locationLine = "%" + self._bookID + " " + chapter + "." + verse + " +1"

							if self._markup_manager._footnote_tracker.hasFootnoteOpenMarkerInLine(line) == True :
								footnoteCount +=1

							verseCount +=1

						else :
							verseCount +=1

						wordCount += len(wordsInLine)

					else :

						# Need to do some checking on other elements in
						# the line. If a footnote marker is found we
						# will go on to the next line. Otherwise we'll
						# ship this one out. (Don't want to break up \f)
						if line.find(footnoteOpenMarker) < 0 :
							self.writeAdjLine(verseCount, footnoteCount, \
								wordCount, locationLine, paragraphType, \
								adjustParaLength, outputObject)

						# Paragraph gets turned off now. We are only
						# looking for paragraph-type text containers.
						paragraph = "off"
						verseCount = 0
						footnoteCount = 0
						wordCount = 0
						paragraphType = ""
						locationLine = ""

			# We'll just go one level deep on poetry (\q should be \q1)
			if len(wordsInLine) > 0 :
				if wordsInLine[0]	== "\\" + self._paragraphMarkers['paragraphNormal'] or \
					wordsInLine[0]	== "\\" + self._paragraphMarkers['paragraphLeft'] or \
					wordsInLine[0]	== "\\" + self._poetryMarkers['poeticLineOne'] :
					paragraph	 = "on"

					if self._markup_manager._footnote_tracker.hasFootnoteOpenMarkerInLine(line) == True :

						footnoteCount +=1

					wordCount += len(wordsInLine)
					if wordsInLine[0]	== "\\" + self._paragraphMarkers['paragraphNormal'] :
						paragraphType	 = self._paragraphMarkers['paragraphNormal']
					elif wordsInLine[0]	== "\\" + self._paragraphMarkers['paragraphLeft'] :
						paragraphType	 = self._paragraphMarkers['paragraphLeft']
					elif wordsInLine[0]	== "\\" + self._poetryMarkers['poeticLineOne'] :
						paragraphType	 = self._poetryMarkers['poeticLineOne']
					else :
						paragraphType	 = "##"
					continue


		# Clean up! Write out the last line now that we are done.
		# As before, we need to do some checking on other elements in
		# the line. If a footnote marker is found we will go on to
		# the next line. Otherwise we'll ship this one out. (Don't
		# want to break up a \f)
		if line.find(footnoteOpenMarker) < 0 :
			self.writeAdjLine(verseCount, footnoteCount, wordCount, \
				locationLine, paragraphType, adjustParaLength, outputObject)


		# All done, tell the world what we did
		self._log_manager.log("INFO", "Paragraph limit set to: " + str(adjustParaLength))
		self._log_manager.log("INFO", "Created paragraph adjustment file: " + self._outputFile)
		self._log_manager.log("INFO", "Lines written =  " + str(self._adjustLinesWritten))


# This starts the whole process going
def doIt(log_manager):

	thisModule = MakeParaAdjustFile(log_manager)
	return thisModule.main()
