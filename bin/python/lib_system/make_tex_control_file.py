#!/usr/bin/python
# -*- coding: utf-8 -*-
# version: 20090120
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# Generate a TeX control file for Scripture processing. The
# data for this proccess is all kept in the project.conf file.
# There are 4 types of TeX control (setup) files needed.
#
#   1) The first one is the common global settins file that
#      controls the parameters for the publication like fonts
#      and page size.
#
#   2) The second is the main control file for each type of
#      text such as front matter, back matter and main
#      contents. This will contain settings for each of these
#      types of text and control things like columns, verse
#      number formats, etc.
#
#   3) The third type is the custom control file which contains
#      settings and macros for the project. This file can be
#      used to override settings in the first two if necessary
#      but that is not recomended.
#
#   4) The fourth type is the control file for the specific
#      object that is being typeset. This is a simple file
#      that contains links to the other three types of
#      control files. Except for the custom control file,
#      all are auto generated and should not be edited for any
#      reason.


# History:
# 20090209 - djd - Initial draft
# 20100212 - djd - Add in auto-TOC code


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

		log_manager._currentSubProcess = 'MkContFile'
		self._log_manager = log_manager
		self._outputFileName = log_manger._currentOutput
		self._inputFileName = log_manager._currentInput
		# Note we get the value from the input file field
		self._contextFlag = log_manager._optionalPassedVariable
		self._flags = ('front', 'bible', 'back')
		self._publicationType = log_manager._publicationType
		self._contextBibleFileName = log_manager._settings['Process']['Files']['FILE_TEX_BIBLE']
		texSettings = log_manager._settings['Process']['Files']['FILE_TEX_SETUP']

		if self._publicationType.lower() == 'scripture' :

			# Decide which file we are needing to make, then direct it to
			# the right function.
			if texSettings == self._outputFileName :
				# This is the project-wide setup file
				makeTheSettingsFile()

			elif self._contextFlag in self._flags :
				# This contains TeX settings information for text to
				# be processed in specific contexts.
				makeTheContextSettingsFile()

			else :
				# This is the control file that links the object
				# to the other settings files
				makeTheControlFile()

		else :
			log_manager.log("ERRR", "Publication type: " + self._publicationType + " is unknown. Process halted.")

#########################################################################################

	def makeTheControlFile (self) :
		'''This is the control file for a specific object that we
			will be typesetting. This contains pointers to the
			other control files that contain the settings
			TeX will work with and it may contain specific
			instructions for this object that can be added
			in an automated way.'''

		settings = '\\input ' + self._outputFileName + '\n'
		# Make a link to the override stylesheet
		settings = settings + '\\stylesheet{' + self._inputFileName + '.sty}\n'

		# Being passed here means the contextFlag was not empty. That
		# being the case, it must be a scripture book. Otherwise, it is
		# a peripheral control file.
		if self._contextFlag != '' :

			settings = settings + '\\input ' + self._contextBibleFileName + '\n'

			# Since we were passed here it is assmumed that the context
			# flag will contain a book ID, not a context marker. We will
			# make a list of them here but the list may contain only one
			# book ID.
			componentScripture = self._contextFlag.split()

			# This will apply the \OmitChapterNumbertrue to only the books
			# that consist of one chapter. Or, if the omitAllChapterNumbers
			# setting is true, it takes the chapter numbers out of all books.
			# To be safe, it turns it off after the book is processed so it
			# will not affect the next book being processed. This is the last
			# write to the output file.
			for book in componentScripture :
				thisBook = pathToText + '/' + book.lower() + '.usfm'
				bookInfo = self.parseThisBook(thisBook)
				if oneChapOmmitRule == 'true' and bookInfo['chapCount'] == 1 or omitAllChapterNumbers == 'true':
					settings = settings + '\\OmitChapterNumbertrue\n'
					settings = settings + '\\ptxfile{' + thisBook + '}\n'
					settings = settings + '\\OmitChapterNumberfalse\n'
				else :
					settings = settings + '\\ptxfile{' + thisBook + '}\n'
		else :



		# Ship the results, change order as needed
		self.writeOutTheFile(self._outputFileName, settings + '\\bye\n')

#########################################################################################

	def makeTheSettingsFile (self) :
		'''This will create the global settings file that other control
			files will link to. This setting file will contain
			settings that are universal to the project. Settings
			for specific parts of the project are found in setup
			files that are made by the makeTheContentSettingsFile()
			elsewhere in this module.'''

		# Build some paths and file names
		texMacros = log_manager._settings['Process']['Files'].get('FILE_TEX_MACRO', 'paratext2.tex')
		setupFile = os.getcwd() + "/" + log_manager._settings['Process']['Files'].get('FILE_TEX_SETUP', 'auto-tex.txt')
		customSetup = os.getcwd() + "/" + log_manager._settings['Process']['Files'].get('FILE_TEX_SETUP_CUSTOM', 'custom-tex.txt')
		styleFile = os.getcwd() + "/" + log_manager._settings['Process']['Files'].get('FILE_TEX_STYLE', 'project.sty')

		# Bring in page format settings
		cropmarks = log_manager._settings['Format']['PageLayout'].get('CROPMARKS', 'true')
		pageHeight = log_manager._settings['Format']['PageLayout'].get('pageHeight', '210mm')
		pageWidth = log_manager._settings['Format']['PageLayout'].get('pageWidth', '148mm')
\endbooknoejecttrue (endBookNoEject)
# Columns
\TitleColumns=1
\IntroColumns=1
\BodyColumns=2
\def\ColumnGutterFactor{15}
\ColumnGutterRuletrue
\ColumnGutterRuleSkip=4pt
# Margins
\MarginUnit=12mm
\def\TopMarginFactor{1.75}
\def\BottomMarginFactor{0} - if set to 0 it will not show up in the output
\def\SideMarginFactor{1.0}
\BindingGutter=12mm
\BindingGuttertrue (useBindingGutter)
# HeaderFooter
\def\HeaderPosition{.75}
\def\FooterPosition{.5}
# Fonts
\def\regular{"[../Fonts/CharisSIL/CharisSILR.ttf]/GR"}
\def\bold{"[../Fonts/CharisSIL/CharisSILB.ttf]/GR"}
\def\italic{"[../Fonts/CharisSIL/CharisSILI.ttf]/GR"}
\def\bolditalic{"[../Fonts/CharisSIL/CharisSILBI.ttf]/GR"}
\tracinglostchars=1 (tracingLostCharacters)
\FontSizeUnit=1pt (fontSizeUnit)
\def\LineSpacingFactor{1.1} (lineSpacingFactor)
\def\VerticalSpaceFactor{1} (verticalSpaceFactor)
\XeTeXlinebreaklocale "G" (xetexLineBreakLocale - false)
# Paths
\PicPath={Illustrations/} (PATH_ILLUSTRATIONS)

\FigurePlaceholderstrue (useFigurePlaceholders)

		# Create the file header
		header = "% tex_settings.txt\n\n% This is an auto-generated file, do not edit. Any necessary changes\n" + \
				"% should be made to the project.conf file or the custom TeX setup file.\n\n"


		# Output to the new makefile file
		# Create the new TeX settings object (overwrite the old file)
		settingsFileObject = codecs.open(setupFile, 'w', encoding='utf_8_sig')
		settingsFileObject.write(header)
		# This connects the system with the custom macro code
		settingsFileObject.write('\\input ' + texMacros + '\n')
		# Add page format settings
		settingsFileObject.write('\\PaperHeight=' + pageHeight + '\n')
		settingsFileObject.write('\\PaperWidth=' + pageWidth + '\n')



		# Now put out the custom macro file path (this may need to be moved)
		settingsFileObject.write('\\input ' + customSetup + '\n')
		# Add some format features here
		if cropmarks.lower() == 'true' :
			settingsFileObject.write('\\CropMarkstrue\n')

		# Add the global style sheet
		settingsFileObject.write('\\stylesheet{' + styleFile + '}\n')
		settingsFileObject.close()

		# Ship the results, change order as needed
		orderedContents = 	fileHeaderText + \
					fileInput + \
					verseChapterSettings + \
					headerSettings + \
					footerSettings + \
					footnoteSettings + \
					generalSettings) + \
					'\\bye\n'

		self.writeOutTheFile(orderedContents)


#########################################################################################

	def makeTheContextSettingsFile (self) :
		'''For each context that we render text in we need to tell TeX
			what the settings are for that context. This is a context
			sensitive settings file output routine.'''

		# Build some paths, file names and settings. We will
		# pickup the settings blindly here and apply them
		# below depending on the context

		# Process
		pathToText = os.getcwd() + "/" + log_manager._settings['Process']['Paths'].get('PATH_TEXTS', 'Texts')
		pathToHyphen = os.getcwd() + "/" + log_manager._settings['Process']['Paths'].get('PATH_HYPHENATION', 'Hyphenation')
		setupFile = os.getcwd() + "/" + log_manager._settings['Process']['Files'].get('FILE_TEX_SETUP', 'auto-tex.txt')
		hyphenFile = pathToHyphen + "/" + log_manager._settings['Process']['Files'].get('FILE_HYPHENATION_TEX', '')
		marginalVerses = log_manager._settings['Process']['Files'].get('FILE_MARGINAL_VERSES', 'ptxplus-marginalverses.tex')
		useHyphenation = log_manager._settings['Process']['Hyphenation'].get('useHyphenation', 'true')
		tocTitle = log_manager._settings['Process']['TOC'].get('mainTitle', 'Table of Contents')

		# Format -> PageLayout
		usePageBorder = log_manager._settings['Format']['PageLayout'].get('usePageBorder', 'false')
		pageBorderScale = log_manager._settings['Format']['PageLayout'].get('pageBorderScale', '825')
		pageBorderFile = log_manager._settings['Process']['Files'].get('FILE_PAGE_BORDER', 'pageborder.pdf')
		useMarginalVerses = log_manager._settings['Format']['Scripture']['ChapterVerse'].get('useMarginalVerses', 'false')
		oneChapOmmitRule = self._log_manager._settings['Format']['Scripture']['ChapterVerse'].get('shortBookChapterOmit', 'true')
		omitAllChapterNumbers = self._log_manager._settings['Format']['Scripture']['ChapterVerse'].get('omitAllChapterNumbers', 'false')

		# Format -> Scripture
		columnshift = log_manager._settings['Format']['Scripture']['Columns'].get('columnshift', '15')
		useRunningHeaderRule = log_manager._settings['Format']['Scripture']['HeaderFooter'].get('useRunningHeaderRule', 'false')
		runningHeaderRulePosition = log_manager._settings['Format']['Scripture']['HeaderFooter'].get('runningHeaderRulePosition', '6')
		verseRefs = log_manager._settings['Format']['Scripture']['HeaderFooter']['HeaderContent'].get('verseRefs', 'false')
		chapterVerseSeparator = log_manager._settings['Format']['Scripture']['HeaderFooter']['HeaderContent'].get('chapterVerseSeparator', ':')
		omitChapterNumber = log_manager._settings['Format']['Scripture']['HeaderFooter']['HeaderContent'].get('omitChapterNumber', 'false')
		omitVerseNumberOne = log_manager._settings['Format']['Scripture']['HeaderFooter']['HeaderContent'].get('omitVerseNumberOne', 'true')
		afterVerseSpaceFactor = log_manager._settings['Format']['Scripture']['HeaderFooter']['HeaderContent'].get('afterVerseSpaceFactor', '2')
		afterChapterSpaceFactor = log_manager._settings['Format']['Scripture'][''].get('afterChapterSpaceFactor', '3')
		removeIndentAfterHeading = log_manager._settings['Format']['Scripture'][''].get('removeIndentAfterHeading', 'false')
		adornVerseNumber = log_manager._settings['Format']['Scripture'][''].get('adornVerseNumber', 'false')

		# Running Header
		runningHeaderTitleLeft = log_manager._settings['Format']['Scripture']['HeaderFooter']['HeaderContent'].get('runningHeaderTitleLeft', 'empty')
		runningHeaderTitleCenter = log_manager._settings['Format']['Scripture']['HeaderFooter']['HeaderContent'].get('runningHeaderTitleCenter', 'empty')
		runningHeaderTitleRight = log_manager._settings['Format']['Scripture']['HeaderFooter']['HeaderContent'].get('runningHeaderTitleRight', 'empty')
		runningHeaderOddLeft = log_manager._settings['Format']['Scripture']['HeaderFooter']['HeaderContent'].get('runningHeaderOddLeft', 'empty')
		runningHeaderOddCenter = log_manager._settings['Format']['Scripture']['HeaderFooter']['HeaderContent'].get('runningHeaderOddCenter', 'pagenumber')
		runningHeaderOddRight = log_manager._settings['Format']['Scripture']['HeaderFooter']['HeaderContent'].get('runningHeaderOddRight', 'rangeref')
		runningHeaderEvenLeft = log_manager._settings['Format']['Scripture']['HeaderFooter']['HeaderContent'].get('runningHeaderEvenLeft', 'rangeref')
		runningHeaderOddCenter = log_manager._settings['Format']['Scripture']['HeaderFooter']['HeaderContent'].get('runningHeaderOddCenter', 'pagenumber')
		runningHeaderEvenRight = log_manager._settings['Format']['Scripture']['HeaderFooter']['HeaderContent'].get('runningHeaderEvenRight', 'empty')
		runningFooterTitleLeft = log_manager._settings['Format']['Scripture']['HeaderFooter']['FooterContent'].get('runningFooterTitleLeft', 'empty')
		runningFooterTitleCenter = log_manager._settings['Format']['Scripture']['HeaderFooter']['FooterContent'].get('runningFooterTitleCenter', 'empty')
		runningFooterTitleRight = log_manager._settings['Format']['Scripture']['HeaderFooter']['FooterContent'].get('runningFooterTitleRight', 'empty')
		runningFooterOddLeft = log_manager._settings['Format']['Scripture']['HeaderFooter']['FooterContent'].get('runningFooterOddLeft', 'empty')
		runningFooterOddCenter = log_manager._settings['Format']['Scripture']['HeaderFooter']['FooterContent'].get('runningFooterOddCenter', 'empty')
		runningFooterOddRight = log_manager._settings['Format']['Scripture']['HeaderFooter']['FooterContent'].get('runningFooterOddRight', 'empty')
		runningFooterEvenLeft = log_manager._settings['Format']['Scripture']['HeaderFooter']['FooterContent'].get('runningFooterEvenLeft', 'empty')
		runningFooterEvenCenter = log_manager._settings['Format']['Scripture']['HeaderFooter']['FooterContent'].get('runningFooterEvenCenter', 'empty')
		runningFooterEvenRight = log_manager._settings['Format']['Scripture']['HeaderFooter']['FooterContent'].get('runningFooterEvenRight', 'empty')

		# Footnotes
		autoCallers = log_manager._settings['Format']['Scripture']['Footnotes'].get('autoCallers', '*')
		autoCallerStartChar = log_manager._settings['Format']['Scripture'][''].get('autoCallerStartChar', '97')
		autoCallerNumChars = log_manager._settings['Format']['Scripture'][''].get('autoCallerNumChars', '26')
		useNumericCallersFootnotes = log_manager._settings['Format']['Scripture'][''].get('useNumericCallersFootnotes', 'false')
		useNumericCallersCrossRefs = log_manager._settings['Format']['Scripture'][''].get('useNumericCallersCrossRefs', 'false')
		pageResetCallersFootnotes = log_manager._settings['Format']['Scripture'][''].get('pageResetCallersFootnotes', 'false')
		pageResetCallersCrossRefs = log_manager._settings['Format']['Scripture'][''].get('pageResetCallersCrossRefs', 'false')
		omitCallerInFootnote = log_manager._settings['Format']['Scripture'][''].get('omitCallerInFootnote', 'false')
		omitCallerInCrossRefs = log_manager._settings['Format']['Scripture'][''].get('omitCallerInCrossRefs', 'false')
		paragraphedFootnotes = log_manager._settings['Format']['Scripture'][''].get('paragraphedFootnotes', 'false')
		paragraphedCrossRefs = log_manager._settings['Format']['Scripture'][''].get('paragraphedCrossRefs', 'false')
		footnoteRule = log_manager._settings['Format']['Scripture'][''].get('footnoteRule', 'true')
		justifyPars = log_manager._settings['Format']['Scripture'][''].get('justifyPars', 'true')
		rightToLeft = log_manager._settings['Format']['Scripture'][''].get('rightToLeft', 'false')

		# Generate a TOC file name.
		tocFile = ''
		if bookID.lower() == 'nt' :
			bookID = self._log_manager._settings['Process']['Binding']['MATTER_OT']
			tocFile = log_manager._settings['Process']['Files']['FILE_AUTO_TOC'] + '-ot.usfm'
		elif bookID.lower() == 'nt' :
			bookID = self._log_manager._settings['Process']['Binding']['MATTER_NT']
			tocFile = log_manager._settings['Process']['Files']['FILE_AUTO_TOC'] + '-nt.usfm'

		# Build our output - These are the strings we will fill:
		fileHeaderText = ''
		fileInput = ''
		verseChapterSettings = ''
		headerSettings = ''
		footerSettings = ''
		footnoteSettings = ''
		generalSettings = ''


		# The file header telling users not to touch it
		fileHeaderText = "This is the " + self._texControlFile + " and it is auto generated. If you know what's good for you, don't edit it!\n\n"

		# FileInput section
		fileInput = '\\input ' + setupFile + '\n'

		# Hyphenation is optional project-wide. There may be some objects that
		# need it and others that do not. That is why it is here at the object level.
		if useHyphenation.lower() == 'true' :
			fileInput = fileInput + '\\input ' + hyphenFile + '\n'

		# Will we use marginal verses?
		if useMarginalVerses.lower() == 'true' :
			fileInput = fileInput + '\\input ' + marginalVerses + '\n'
			fileInput = fileInput + '\\columnshift=' + columnshift + '\n'

		# First off, if a file name for the TOC is found, write it out
		if tocFile != "" :
			fileInput = fileInput + '\\GenerateTOC[' + tocTitle + ']{' + tocFile + '}\n'

		# Do we want a page border?
		if usePageBorder.lower() == 'true' :
			fileInput = fileInput + '\\def\\PageBorder{' + pageBorderFile + ' scaled ' + pageBorderScale + '}\n'

		# Verse/chapter settings
		if verseRefs.lower() == 'true' :
			verseChapterSettings = verseChapterSettings + '\\VerseRefstrue\n'

		if omitChapterNumber.lower() == 'true' :
			verseChapterSettings = verseChapterSettings + '\\OmitChapterNumberRHtrue\n'

		if omitVerseNumberOne.lower() == 'true' :
			verseChapterSettings = verseChapterSettings + '\\OmitVerseNumberOnetrue\n'

		if removeIndentAfterHeading.lower() == 'true' :
			verseChapterSettings = verseChapterSettings + '\\IndentAfterHeadingtrue\n'

		if adornVerseNumber.lower() == 'true' :
			verseChapterSettings = verseChapterSettings + '\\def\AdornVerseNumber#1{(#1)}\n'

		verseChapterSettings = verseChapterSettings + '\\def\ChapterVerseSeparator{' + chapterVerseSeparator + '}\n'
		verseChapterSettings = verseChapterSettings + '\\def\AfterVerseSpaceFactor{' + afterVerseSpaceFactor + '}\n'
		verseChapterSettings = verseChapterSettings + '\\def\AfterChapterSpaceFactor{' + afterChapterSpaceFactor + '}\n'

		# Header settings
		if useRunningHeaderRule.lower() == 'true' :
			headerSettings = headerSettings + '\\RHruleposition=' + runningHeaderRulePosition + '\n'

		headerSettings = headerSettings + '\\def\\RHtitleleft{\\' + runningHeaderTitleLeft + '}\n'
		headerSettings = headerSettings + '\\def\\RHtitlecenter{\\' + runningHeaderTitleCenter + '}\n'
		headerSettings = headerSettings + '\\def\\RHtitleright{\\' + runningHeaderTitleRight + '}\n'
		headerSettings = headerSettings + '\\def\\RHoddleft{\\' + runningHeaderOddLeft + '}\n'
		headerSettings = headerSettings + '\\def\\RHoddcenter{\\' + runningHeaderOddCenter + '}\n'
		headerSettings = headerSettings + '\\def\\RHoddright{\\' + runningHeaderOddRight + '}\n'
		headerSettings = headerSettings + '\\def\\RHevenleft{\\' + runningHeaderEvenLeft + '}\n'
		headerSettings = headerSettings + '\\def\\RHevencenter{\\' + runningHeaderOddCenter + '}\n'
		headerSettings = headerSettings + '\\def\\RHevenright{\\' + runningHeaderEvenRight + '}\n'

		# Footer settings
		footerSettings = footerSettings + '\\def\\RFtitleleft{\\' + runningFooterTitleLeft + '}\n'
		footerSettings = footerSettings + '\\def\\RFtitlecenter{\\' + runningFooterTitleCenter + '}\n'
		footerSettings = footerSettings + '\\def\\RFtitleright{\\' + runningFooterTitleRight + '}\n'
		footerSettings = footerSettings + '\\def\\RFoddleft{\\' + runningFooterOddLeft + '}\n'
		footerSettings = footerSettings + '\\def\\RFoddcenter{\\' + runningFooterOddCenter + '}\n'
		footerSettings = footerSettings + '\\def\\RFoddright{\\' + runningFooterOddRight + '}\n'
		footerSettings = footerSettings + '\\def\\RFevenleft{\\' + runningFooterEvenLeft + '}\n'
		footerSettings = footerSettings + '\\def\\RFevencenter{\\' + runningFooterEvenCenter + '}\n'
		footerSettings = footerSettings + '\\def\\RFevenright{\\' + runningFooterEvenRight + '}\n'

		# Footnote settings
		# If we use Autocallers we need to leave out some other things and vise versa
		if autoCallers != '' :
			footnoteSettings = footnoteSettings + '\\AutoCallers{f}{\kern0.2em*\kern0.4em} (autoCallers) (if this, don't use some other things)

		else :
			footnoteSettings = footnoteSettings + '\\def\\AutoCallerStartChar{' + autoCallerStartChar + '}\n'
			footnoteSettings = footnoteSettings + '\\def\\AutoCallerNumChars{' + autoCallerNumChars + '}\n'
			if useNumericCallersFootnotes.lower() == 'true' :
				footnoteSettings = footnoteSettings + '\\NumericCallers{f}\n'
			if useNumericCallersCrossRefs.lower() == 'true' :
				footnoteSettings = footnoteSettings + '\\NumericCallers{x}\n'
			if pageResetCallersFootnotes.lower() == 'true' :
				footnoteSettings = footnoteSettings + '\\PageResetCallers{f}\n'
			if pageResetCallersCrossRefs.lower() == 'true' :
				footnoteSettings = footnoteSettings + '\\PageResetCallers{x}\n'

		if footnoteRule.lower() == 'true' :
			footnoteSettings = footnoteSettings + '\\def\\footnoterule{}\n'


		footnoteSettings = footnoteSettings +

*\OmitCallerInNote{f} (omitCallerInFootnote)
*\OmitCallerInNote{x} (omitCallerInCrossRefs)
*\ParagraphedNotes{f} (paragraphedFootnotes)
*\ParagraphedNotes{x} (paragraphedCrossRefs)

		# General settings
*\JustifyParsfalse (justifyPars = true)
*\RTLtrue (rightToLeft)


		# Ship the results, change order as needed
		orderedContents = 	fileHeaderText + \
					fileInput + \
					verseChapterSettings + \
					headerSettings + \
					footerSettings + \
					footnoteSettings + \
					generalSettings) + \
					'\\bye\n'

		self.writeOutTheFile(orderedContents)



	def writeOutTheFile (self, contents) :
		'''Write out the file.'''

		texControlObject = codecs.open(self._outputFileName, "w", encoding='utf_8_sig')
		texControlObject.write(contents)
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
