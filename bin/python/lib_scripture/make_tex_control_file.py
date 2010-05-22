#!/usr/bin/python
# -*- coding: utf-8 -*-
# version: 20090120
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# Generate a TeX control file for Scripture processing. This
# is designed to work with individual control files or will
# create a control file for processing a number of book files.


# History:
# 20090209 - djd - Initial draft
# 20100212 - djd - Add auto-TOC code


#############################################################
######################### Shell Class #######################
#############################################################

import codecs, os
import parse_sfm

# Import supporting local classes
from encoding_manager import *
from tools import *
tools = Tools()


class MakeTexControlFile (object) :

	def main (self, log_manager) :

		self._log_manager = log_manager
		texControlFile = log_manager._currentOutput
		bookID = log_manager._currentTargetID
		log_manager._currentSubProcess = 'MkContFile'

		# Build some paths, file names and settings
		pathToText = os.getcwd() + "/" + log_manager._settings['Process']['Paths'].get('PATH_TEXTS', 'Texts')
		pathToHyphen = os.getcwd() + "/" + log_manager._settings['Process']['Paths'].get('PATH_HYPHENATION', 'Hyphenation')
		setupFile = os.getcwd() + "/" + log_manager._settings['Process']['Files'].get('FILE_TEX_SETUP', 'auto-tex.txt')
		hyphenFile = pathToHyphen + "/" + log_manager._settings['Process']['Files'].get('FILE_HYPHENATION_TEX', '')
		marginalVerses = log_manager._settings['Process']['Files'].get('FILE_MARGINAL_VERSES', 'ptxplus-marginalverses.tex')

\columnshift=15pt
\def\PageBorder{tuborder.pdf scaled 825} (usePageBorder / pageBorderScale)
useRunningHeaderRule
\RHruleposition=6pt (runningHeaderRulePosition)
\VerseRefstrue (verseRefs)
\OmitChapterNumberRHtrue (omitChapterNumber)
\def\RHtitleleft{\empty} (runningHeaderTitleLeft)
\def\RHtitlecenter{\empty} (runningHeaderTitleCenter)
\def\RHtitleright{\empty} (runningHeaderTitleRight)
\def\RHoddleft{\empty} (runningHeaderOddLeft)
\def\RHoddcenter{\pagenumber} (runningHeaderOddCenter)
\def\RHoddright{\rangeref} (runningHeaderOddRight)
\def\RHevenleft{\rangeref} (runningHeaderEvenLeft)
\def\RHevencenter{\pagenumber} (runningHeaderOddCenter)
\def\RHevenright{\empty} (runningHeaderEvenRight)
\def\RFtitleleft{\empty} (runningFooterTitleLeft)
\def\RFtitlecenter{\empty} (runningFooterTitleCenter)
\def\RFtitleright{\empty} (runningFooterTitleRight)
\def\RFoddleft{\empty} (runningFooterOddLeft)
\def\RFoddcenter{\empty} (runningFooterOddCenter)
\def\RFoddright{\empty} (runningFooterOddRight)
\def\RFevenleft{\empty} (runningFooterEvenLeft)
\def\RFevencenter{\empty} (runningFooterEvenCenter)
\def\RFevenright{\empty} (runningFooterEvenRight)

# Footnote settings
%\AutoCallerStartChar{}
%\AutoCallerNumChars{}
%\AutoCallers{f}{\kern0.2em*\kern0.4em}
%\NumericCallers{x}
%\PageResetCallers{x}
%\OmitCallerInNote{f}
%\ParagraphedNotes{f}
%\def\footnoterule{}

% Footnote caller kerning - To adjust space around the
% footnote caller use the following code Adjust the kern
% amounts as necessary
%\let\OriginalGetCaller=\getcaller
%\def\getcaller#1#2{%
%  \kern0.2em\OriginalGetCaller{#1}{#2}\kern0.4em}

% Inter Note Skip - Adjust the horizontal space between footnotes,
% both paragraphed and non-paragraphed
\catcode`\@=11
  \intern@teskip=10pt
\catcode`\@=12

\def\internotepenalty{9999}


		useHyphenation = log_manager._settings['Process']['Hyphenation'].get('useHyphenation', 'true')
		useMarginalVerses = log_manager._settings['Format']['Scripture']['ChapterVerse'].get('useMarginalVerses', 'false')
		tocTitle = log_manager._settings['Process']['TOC'].get('mainTitle', 'Table of Contents')

#######################################################################################################
# we need some kind of test to see if this is a control file for Scripture so we can build contextually

		# Look for settings to apply, not all of them will be
		# usable in every case
		try :
			oneChapOmmitRule = self._log_manager._settings['Format']['Scripture']['ChapterVerse']['shortBookChapterOmit']
		except :
			oneChapOmmitRule = "false"

		# Output the bookWordlist to the bookWordlist file (we'll overwrite the existing one)
		texControlObject = codecs.open(texControlFile, "w", encoding='utf_8_sig')

		# Read in all the global settings
		texControlObject.write('\\input ' + setupFile + '\n')

		# Hyphenation is optional project-wide. There may be some objects that
		# need it and others that do not. That is why it is here at the object level.
		if useHyphenation.lower() == 'true' :
			texControlObject.write('\\input ' + hyphenFile + '\n')
		# Other options that can be added in the file
		# Note that order is important, though not fully understood :-)
		if useMarginalVerses.lower() == 'true' :
			texControlObject.write('\\input ' + marginalVerses + '\n')
			texControlObject.write('\\input ' + \columnshift=15pt

		# Passing in all the book IDs is problematic we can get that
		# information from the .config file so we'll use a syntax
		# shortcut to indicate which one we are looking for.
		# Check for nt or ot and write out a ptxfile line for each
		# book ID found. Otherwise just write out for a single book
		tocFile = ""
		if bookID.lower() == "ot" :
			bookID = self._log_manager._settings['Process']['Binding']['MATTER_OT']
			tocFile = log_manager._settings['Process']['Files']['FILE_AUTO_TOC'] + "-ot.usfm"
		elif bookID.lower() == "nt" :
			bookID = self._log_manager._settings['Process']['Binding']['MATTER_NT']
			tocFile = log_manager._settings['Process']['Files']['FILE_AUTO_TOC'] + "-nt.usfm"

		# Here we will add some custom commands for things that we
		# need more contextual control over.

		# First off, if a file name for the TOC is found, write it out
		if tocFile != "" :
			texControlObject.write('\\GenerateTOC[' + tocTitle + ']{' + tocFile + '}\n')

		componentScripture = bookID.split()
		for book in componentScripture :
			thisBook = pathToText + '/' + book.lower() + '.usfm'
			bookInfo = self.parseThisBook(thisBook)
			if oneChapOmmitRule == "true" and bookInfo['chapCount'] == 1 :
				texControlObject.write('\\OmitChapterNumbertrue\n')
				texControlObject.write('\\ptxfile{' + thisBook + '}\n')
				texControlObject.write('\\OmitChapterNumberfalse\n')
			else :
				texControlObject.write('\\ptxfile{' + thisBook + '}\n')
		texControlObject.write('\\bye\n')
		texControlObject.close()

	def parseThisBook (self, book) :
		'''Parse a specific book based on ID then return relevant info.'''

		# Get our current book object
		bookObject = "".join(codecs.open(book, "r", encoding='utf_8_sig'))

		# Load in the parser
		parser = parse_sfm.Parser()

		# Set some vars to pass
		info = {}
		chapCount = 0

		# This calls a custom version of the handler for this script
		handler = MakeTexControlFileHandler(self._log_manager, chapCount)
		parser.setHandler(handler)
		parser.parse(bookObject)

		info['chapCount'] = handler._chapCount

		return info

class MakeTexControlFileHandler (parse_sfm.Handler) :
	'''This class replaces the Handler class in the parse_sfm module.'''

	def __init__(self, log_manager, chapCount) :

		self._log_manager = log_manager
		self._book = ""
		self._chapCount = chapCount


	def start (self, tag, num, info, prefix) :
		'''This tells us when a tag starts. We will use this information to set location
			and trigger events.'''

		# Track the location
		self._log_manager.setLocation(self._book, tag, num)

		# Right now, a chapter count is about the only thing we will be doing
		if tag == "c" :
			self._chapCount = int(num)

		if num != "" :
			return "\\" + tag + " " + num
		else :
			return "\\" + tag


	def text (self, text, tag, info) :
		'''This function allows us to harvest the text from a given text element
			if needed.'''

		# Get the book id for setting our location in start()
		if tag == 'id' :
			self._book = text

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


# This starts the whole process going
def doIt (log_manager) :

	thisModule = MakeTexControlFile()
	return thisModule.main(log_manager)
