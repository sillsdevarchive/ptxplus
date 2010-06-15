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
# BTW, this will only work with the ptx2pdf macro package.


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
		'''This part is all about direction. In this function we will figure out
			what kind of settings file needs to be made and then call the
			right function to do it.'''

		log_manager._currentSubProcess = 'MkTexContFile'
		self._log_manager = log_manager
		self._outputFile = log_manager._currentOutput
		self._inputFile = log_manager._currentInput
		self._inputID = log_manager._currentTargetID
		self._pathToText = os.getcwd() + "/" + self._log_manager._settings['Process']['Paths'].get('PATH_TEXTS', 'Texts')
		self._pathToProcess = os.getcwd() + "/" + self._log_manager._settings['Process']['Paths'].get('PATH_PROCESS', 'Process')
		self._pathToIllustrations = os.getcwd() + "/" + self._log_manager._settings['System']['Paths'].get('PATH_ILLUSTRATIONS', 'Illustrations')
		self._texMacros = self._log_manager._settings['System']['Files'].get('FILE_TEX_MACRO', 'paratext2.tex')
		self._cvSettingsFile = self._log_manager._settings['System']['Files'].get('FILE_TEX_COVER', '.cover_settings.txt')
		self._fmSettingsFile = self._log_manager._settings['System']['Files'].get('FILE_TEX_FRONT', '.front_settings.txt')
		self._biSettingsFile = self._log_manager._settings['System']['Files'].get('FILE_TEX_BIBLE', '.bible_settings.txt')
		self._bmSettingsFile = self._log_manager._settings['System']['Files'].get('FILE_TEX_BACK', '.back_settings.txt')
		self._cmSettingsFile = self._pathToProcess + "/" + self._log_manager._settings['System']['Files'].get('FILE_TEX_CUSTOM', 'custom-tex.txt')
		self._txSettingsFile = self._log_manager._settings['System']['Files'].get('FILE_TEX_SETUP', '.setup_tex.txt')
		# Note we get the value from the input file field
		self._contextFlag = log_manager._optionalPassedVariable
		self._flags = ('project', 'cover', 'front', 'bible', 'back', 'periph')
		self._frontMatter = self._log_manager._settings['System']['Binding']['MATTER_FRONT'].split()
		self._backMatter = self._log_manager._settings['System']['Binding']['MATTER_BACK'].split()
		self._coverMatter = self._log_manager._settings['System']['Binding']['MATTER_COVER'].split()
		self._otMatter = self._log_manager._settings['System']['Binding']['MATTER_OT'].split()
		self._ntMatter = self._log_manager._settings['System']['Binding']['MATTER_NT'].split()
		self._publicationType = log_manager._publicationType
		# File extentions (Expand this, more will be needed in the future)
		self._extStyle = self._log_manager._settings['System']['Extensions'].get('EXT_STYLE', 'sty')
		# Some lists
		self._headerPositions = ['RHtitleleft', 'RHtitlecenter', 'RHtitleright', \
						'RHoddleft', 'RHoddcenter', 'RHoddright', \
						'RHevenleft', 'RHevencenter', 'RHevenright']
		self._footerPositions = ['RFtitleleft', 'RFtitlecenter', 'RFtitleright', \
						'RFoddleft', 'RFoddcenter', 'RFoddright', \
						'RFevenleft', 'RFevencenter', 'RFevenright']


		if self._publicationType.lower() == 'scripture' :
			# Decide which file we are needing to make, then direct it to
			# the right function.

			if self._txSettingsFile in self._outputFile.split('/') :
				# This is the project-wide setup file that contains
				# general project parameters
				self.makeTheSettingsFile()

			elif self._contextFlag in self._flags and self._contextFlag != 'periph' :
				# This contains TeX settings information for text to
				# be processed in specific contexts.
				self.makeTheContextSettingsFile()

			else :
				# This is the control file that links the object
				# to the other settings files
				self.makeTheControlFile()

		else :
			self._log_manager.log("ERRR", "Publication type: " + self._publicationType + " is unknown. Process halted.")
			return

#########################################################################################

	def makeTheControlFile (self) :
		'''This is the control file for a specific object that we
			will be typesetting. This contains pointers to the
			other control files that contain the settings
			TeX will work with and it may contain specific
			instructions for this object that can be added
			in an automated way.'''

		# Get a couple settings
		oneChapOmmitRule = self._log_manager._settings['Format']['Scripture']['ChapterVerse'].get('shortBookChapterOmit', 'true')
		omitAllChapterNumbers = self._log_manager._settings['Format']['Scripture']['ChapterVerse'].get('omitAllChapterNumbers', 'false')
		useHyphenation = self._log_manager._settings['System']['Hyphenation'].get('useHyphenation', 'true')
		pathToHyphen = os.getcwd() + "/" + self._log_manager._settings['System']['Paths'].get('PATH_HYPHENATION', 'Hyphenation')
		hyphenFile = pathToHyphen + "/" + self._log_manager._settings['System']['Files'].get('FILE_HYPHENATION_TEX', 'hyphenation.tex')
		bibleStyleFile = self._pathToProcess + '/' + self._log_manager._settings['System']['Files'].get('FILE_BIBLE_STYLE', 'bible.sty')

		# Input the main macro set here in the control file
		settings = '\\input ' + self._texMacros + '\n'

		# All local control files will link to the main settings file
		settings = settings + '\\input ' + self._txSettingsFile + '\n'

		# Now link to the custom settings file. As this can override some
		# settings it seems that it would be best for it to come near the end
		# of the initialization process. The control file would be the best
		# place to bing it in.
		settings = settings + '\\input ' + self._cmSettingsFile + '\n'

		# Make a link to the local override stylesheet. This file can override
		# styles that were introduced in the main setup file. For major
		# sections like the OT and NT, we have a bible.sty style sheet at
		# this level. This is an override style sheet for Scripture material.
		# Only Scriture matter will have an ID so if it has one we will
		# output the bible.sty override file. Otherwise, we output a custom
		# style override file.
		if self._inputID != '' :
			settings = settings + '\\stylesheet{' + bibleStyleFile + '}\n'
		else :
			settings = settings + '\\stylesheet{' + self._pathToProcess + "/" + self._inputFile + '.' + self._extStyle + '}\n'

		# Being passed here means the contextFlag was not empty. That
		# being the case, it must be a scripture book. Otherwise, it is
		# a peripheral control file.
		if self._contextFlag not in self._flags :

			settings = settings + '\\input ' + self._biSettingsFile + '\n'

			# Hyphenation is optional project-wide so we will put it here. However,
			# we might need to rethink this.
			if useHyphenation.lower() == 'true' :
				settings = settings + '\\input ' + hyphenFile + '\n'

			# Since we were passed here it is assmumed that the context
			# flag will contain a book ID, or will represent the entire
			# new or old testament which we will handle different.
			# If it isn't a NT or OT marker, then we assume it is a
			# single book and we will only process that one book based
			# on the book ID given.
			componentScripture = []
			if self._inputID == 'ot' :
				componentScripture = self._otMatter
			elif self._inputID == 'nt' :
				componentScripture = self._ntMatter
			else :
				if self._inputID :
					componentScripture = [self._inputID]
				else :
					self._log_manager.log("ERRR", "Not sure how to process the inputID in this context. The inputID is empty. The process has failed.")
					return

			# This will apply the \OmitChapterNumbertrue to only the books
			# that consist of one chapter. Or, if the omitAllChapterNumbers
			# setting is true, it takes the chapter numbers out of all books.
			# To be safe, it turns it off after the book is processed so it
			# will not affect the next book being processed. This is the last
			# write to the output file.
			for book in componentScripture :
				# The file(s) we need to point to in this instance are not
				# found in the inputFile, we have to generate them here.
				thisBook = self._pathToText + '/' + book.lower() + '.usfm'
				bookInfo = self.parseThisBook(thisBook)
				if oneChapOmmitRule == 'true' and bookInfo['chapCount'] == 1 or omitAllChapterNumbers == 'true':
					settings = settings + '\\OmitChapterNumbertrue\n'
					settings = settings + '\\ptxfile{' + thisBook + '}\n'
					settings = settings + '\\OmitChapterNumberfalse\n'
				else :
					settings = settings + '\\ptxfile{' + thisBook + '}\n'

		# If there was no context flag at all that means it has to be peripheral
		# matter. But is is front or back matter. we'll need to test to see
		else :
			if self._inputFile.split('/')[-1] in self._frontMatter :
				settings = settings + '\\input ' + self._fmSettingsFile + '\n'

			elif self._inputFile.split('/')[-1] in self._backMatter :
				settings = settings + '\\input ' + self._bmSettingsFile + '\n'

			elif self._inputFile.split('/')[-1] in self._coverMatter :
				settings = settings + '\\input ' + self._cvSettingsFile + '\n'

			else :
				self._log_manager.log("ERRR", "This module thinks that: " + self._inputFile + " part of the peripheral matter but it cannot find it on either the cover, front or back matter binding lists. Process halted.")
				return

			# For peripheral matter we do not have to generate the name like
			# with Scripture books
			settings = settings + '\\ptxfile{' + self._pathToText + '/' + self._inputFile + '}\n'

		# Combine the results
		settings = settings + '\\bye\n'

		# Ship the results, change order as needed
		self.writeOutTheFile(settings)

#########################################################################################

	def makeTheSettingsFile (self) :
		'''This will create the global settings file that other control
			files will link to. This setting file will contain
			settings that are universal to the project. Settings
			for specific parts of the project are found in setup
			files that are made by the makeTheContentSettingsFile()
			elsewhere in this module.'''

		# Build some paths and file names
		styleFile = self._pathToProcess + "/" + self._log_manager._settings['System']['Files'].get('FILE_TEX_STYLE', '.project.sty')
		# Bring in page format settings
		useCropmarks = self._log_manager._settings['Format']['PageLayout'].get('USE_CROPMARKS', 'true')
		pageHeight = self._log_manager._settings['Format']['PageLayout'].get('pageHeight', '210mm')
		pageWidth = self._log_manager._settings['Format']['PageLayout'].get('pageWidth', '148mm')
		endBookNoEject = self._log_manager._settings['Format']['Scripture']['Columns'].get('endBookNoEject', 'false')
		titleColumns = self._log_manager._settings['Format']['Scripture']['Columns'].get('titleColumns', '1')
		introColumns = self._log_manager._settings['Format']['Scripture']['Columns'].get('introColumns', '1')
		bodyColumns = self._log_manager._settings['Format']['Scripture']['Columns'].get('bodyColumns', '2')
		columnGutterFactor = self._log_manager._settings['Format']['Scripture']['Columns'].get('columnGutterFactor', '15')
		columnGutterRule = self._log_manager._settings['Format']['Scripture']['Columns'].get('columnGutterRule', 'false')
		columnGutterRuleSkip = self._log_manager._settings['Format']['Scripture']['Columns'].get('columnGutterRuleSkip', '4')
		# Margins
		marginUnit = self._log_manager._settings['Format']['Scripture']['Margins'].get('marginUnit', '12')
		topMarginFactor = self._log_manager._settings['Format']['Scripture']['Margins'].get('topMarginFactor', '1.0')
		bottomMarginFactor = self._log_manager._settings['Format']['Scripture']['Margins'].get('bottomMarginFactor', '0')
		sideMarginFactor = self._log_manager._settings['Format']['Scripture']['Margins'].get('sideMarginFactor', '0.7')
		useBindingGutter = self._log_manager._settings['Format']['Scripture']['Margins'].get('useBindingGutter', 'false')
		bindingGutter = self._log_manager._settings['Format']['Scripture']['Margins'].get('bindingGutter', '12mm')
		# Header/Footer
		headerPosition = self._log_manager._settings['Format']['Scripture']['HeaderFooter'].get('headerPosition', '0.5')
		footerPosition = self._log_manager._settings['Format']['Scripture']['HeaderFooter'].get('footerPosition', '0.5')
		# Fonts and text
		xetexLineBreakLocale = self._log_manager._settings['Format']['Fonts'].get('xetexLineBreakLocale', 'false')
		fontDefRegular = self._log_manager._settings['Format']['Fonts'].get('fontDefRegular', '[../Fonts/GenBkBas/GenBkBasR.ttf]/GR')
		fontDefBold = self._log_manager._settings['Format']['Fonts'].get('fontDefBold', '[../Fonts/GenBkBas/GenBkBasB.ttf]/GR')
		fontDefItalic = self._log_manager._settings['Format']['Fonts'].get('fontDefItalic', '[../Fonts/GenBkBas/GenBkBasI.ttf]/GR')
		fontDefBoldItalic = self._log_manager._settings['Format']['Fonts'].get('fontDefBoldItalic', '[../Fonts/GenBkBas/GenBkBasBI.ttf]/GR')
		tracingLostCharacters = self._log_manager._settings['Format']['Fonts'].get('tracingLostCharacters', 'false')
		fontSizeUnit = self._log_manager._settings['Format']['Fonts'].get('fontSizeUnit', '1')
		lineSpacingFactor = self._log_manager._settings['Format']['Fonts'].get('lineSpacingFactor', '1.1')
		verticalSpaceFactor = self._log_manager._settings['Format']['Fonts'].get('verticalSpaceFactor', '1')

		# Build our output - These are the strings we will fill:
		fileHeaderText = ''
		fileInput = ''
		formatSettings = ''
		headerFooterSettings = ''
		fontSettings = ''

		# Create the file header
		fileHeaderText =    "% tex_settings.txt\n\n% This is an auto-generated file, do not edit. Any necessary changes\n" + \
					"% should be made to the project.conf file or the custom TeX setup file.\n\n"
		# Add the global style sheet
		fileInput = fileInput + '\\stylesheet{' + styleFile + '}\n'
		# Add format settings
		formatSettings = '\\PaperHeight=' + pageHeight + '\n'
		formatSettings = formatSettings + '\\PaperWidth=' + pageWidth + '\n'
		if useCropmarks.lower() == 'true' :
			formatSettings = formatSettings + '\\CropMarkstrue\n'
		if endBookNoEject.lower() == 'true' :
			formatSettings = formatSettings + '\\endbooknoejecttrue\n'
		# Columns
		formatSettings = formatSettings + '\\TitleColumns=' + titleColumns + '\n'
		formatSettings = formatSettings + '\\IntroColumns=' + introColumns + '\n'
		formatSettings = formatSettings + '\\BodyColumns=' + bodyColumns + '\n'
		formatSettings = formatSettings + '\\def\\ColumnGutterFactor{' + columnGutterFactor + '}\n'
		if columnGutterRule.lower() == 'true' :
			formatSettings = formatSettings + '\\ColumnGutterRuletrue\n'
		formatSettings = formatSettings + '\\ColumnGutterRuleSkip=' + columnGutterRuleSkip + 'pt\n'
		# Margins
		formatSettings = formatSettings + '\\MarginUnit=' + marginUnit + '\n'
		formatSettings = formatSettings + '\\def\\TopMarginFactor{' + topMarginFactor + '}\n'
		formatSettings = formatSettings + '\\def\\BottomMarginFactor{' + bottomMarginFactor + '}\n'
		formatSettings = formatSettings + '\\def\\SideMarginFactor{' + sideMarginFactor + '}\n'
		if useBindingGutter.lower() == 'true' :
			formatSettings = formatSettings + '\\BindingGuttertrue\n'
			formatSettings = formatSettings + '\\BindingGutter=' + bindingGutter + '\n'
		# HeaderFooter
		headerFooterSettings = headerFooterSettings + '\\def\\HeaderPosition{' + headerPosition + '}\n'
		headerFooterSettings = headerFooterSettings + '\\def\\FooterPosition{' + footerPosition + '}\n'
		# Fonts
		if xetexLineBreakLocale.lower() == 'true' :
			fontSettings = fontSettings + '\\XeTeXlinebreaklocale \"G\"\n'
		fontSettings = fontSettings + '\\def\\regular{\"' + fontDefRegular + '\"}\n'
		fontSettings = fontSettings + '\\def\\bold{\"' + fontDefBold + '\"}\n'
		fontSettings = fontSettings + '\\def\\italic{\"' + fontDefItalic + '\"}\n'
		fontSettings = fontSettings + '\\def\\bolditalic{\"' + fontDefBoldItalic + '\"}\n'
		if tracingLostCharacters.lower() == 'true' :
			fontSettings = fontSettings + '\\tracinglostchars=1\n'
		fontSettings = fontSettings + '\\FontSizeUnit=' + fontSizeUnit + 'pt\n'
		fontSettings = fontSettings + '\\def\\LineSpacingFactor{' + lineSpacingFactor + '}\n'
		fontSettings = fontSettings + '\\def\\VerticalSpaceFactor{' + verticalSpaceFactor + '}\n'

		# Ship the results, change order as needed
		orderedContents =     fileHeaderText + \
					fileInput + \
					formatSettings + \
					headerFooterSettings + \
					fontSettings + \
					'\n'

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
		marginalVersesMacro = self._log_manager._settings['System']['Files'].get('FILE_MARGINAL_VERSES', 'ptxplus-marginalverses.tex')
		useFigurePlaceholders = self._log_manager._settings['Format']['Scripture']['Illustrations'].get('useFigurePlaceholders', 'true')
		autoTocFile = self._log_manager._settings['System']['Paths'].get('FILE_AUTO_TOC', 'auto-toc')
		generateTOC = self._log_manager._settings['System']['TOC'].get('generateTOC', 'true')
		tocTitle = self._log_manager._settings['System']['TOC'].get('mainTitle', 'Table of Contents')
		# Format -> PageLayout
		useIllustrations = self._log_manager._settings['Format']['PageLayout'].get('USE_ILLUSTRATIONS', 'false')
		usePageBorder = self._log_manager._settings['Format']['PageLayout'].get('USE_PAGE_BORDER', 'false')
		pageBorderScale = self._log_manager._settings['Format']['PageLayout'].get('pageBorderScale', '825')
		pageBorderFile = self._log_manager._settings['System']['Files'].get('FILE_PAGE_BORDER', 'pageborder.pdf')
		useMarginalVerses = self._log_manager._settings['Format']['Scripture']['ChapterVerse'].get('useMarginalVerses', 'false')
		# Format -> Scripture
		columnshift = self._log_manager._settings['Format']['Scripture']['Columns'].get('columnshift', '15')
		useRunningHeaderRule = self._log_manager._settings['Format']['Scripture']['HeaderFooter'].get('useRunningHeaderRule', 'false')
		runningHeaderRulePosition = self._log_manager._settings['Format']['Scripture']['HeaderFooter'].get('runningHeaderRulePosition', '6')
		verseRefs = self._log_manager._settings['Format']['Scripture']['HeaderFooter']['HeaderContent'].get('verseRefs', 'false')
		chapterVerseSeparator = self._log_manager._settings['Format']['Scripture']['HeaderFooter']['HeaderContent'].get('chapterVerseSeparator', ':')
		omitChapterNumber = self._log_manager._settings['Format']['Scripture']['HeaderFooter']['HeaderContent'].get('omitChapterNumber', 'false')
		omitVerseNumberOne = self._log_manager._settings['Format']['Scripture']['HeaderFooter']['HeaderContent'].get('omitVerseNumberOne', 'true')
		afterVerseSpaceFactor = self._log_manager._settings['Format']['Scripture']['HeaderFooter']['HeaderContent'].get('afterVerseSpaceFactor', '2')
		afterChapterSpaceFactor = self._log_manager._settings['Format']['Scripture']['ChapterVerse'].get('afterChapterSpaceFactor', '3')
		removeIndentAfterHeading = self._log_manager._settings['Format']['Scripture']['ChapterVerse'].get('removeIndentAfterHeading', 'false')
		adornVerseNumber = self._log_manager._settings['Format']['Scripture']['ChapterVerse'].get('adornVerseNumber', 'false')
		# Running Header
		runningHeaderTitleLeft = self._log_manager._settings['Format']['Scripture']['HeaderFooter']['HeaderContent'].get('runningHeaderTitleLeft', 'empty')
		runningHeaderTitleCenter = self._log_manager._settings['Format']['Scripture']['HeaderFooter']['HeaderContent'].get('runningHeaderTitleCenter', 'empty')
		runningHeaderTitleRight = self._log_manager._settings['Format']['Scripture']['HeaderFooter']['HeaderContent'].get('runningHeaderTitleRight', 'empty')
		runningHeaderOddLeft = self._log_manager._settings['Format']['Scripture']['HeaderFooter']['HeaderContent'].get('runningHeaderOddLeft', 'empty')
		runningHeaderOddCenter = self._log_manager._settings['Format']['Scripture']['HeaderFooter']['HeaderContent'].get('runningHeaderOddCenter', 'pagenumber')
		runningHeaderOddRight = self._log_manager._settings['Format']['Scripture']['HeaderFooter']['HeaderContent'].get('runningHeaderOddRight', 'rangeref')
		runningHeaderEvenLeft = self._log_manager._settings['Format']['Scripture']['HeaderFooter']['HeaderContent'].get('runningHeaderEvenLeft', 'rangeref')
		runningHeaderOddCenter = self._log_manager._settings['Format']['Scripture']['HeaderFooter']['HeaderContent'].get('runningHeaderOddCenter', 'pagenumber')
		runningHeaderEvenRight = self._log_manager._settings['Format']['Scripture']['HeaderFooter']['HeaderContent'].get('runningHeaderEvenRight', 'empty')
		runningFooterTitleLeft = self._log_manager._settings['Format']['Scripture']['HeaderFooter']['FooterContent'].get('runningFooterTitleLeft', 'empty')
		runningFooterTitleCenter = self._log_manager._settings['Format']['Scripture']['HeaderFooter']['FooterContent'].get('runningFooterTitleCenter', 'empty')
		runningFooterTitleRight = self._log_manager._settings['Format']['Scripture']['HeaderFooter']['FooterContent'].get('runningFooterTitleRight', 'empty')
		runningFooterOddLeft = self._log_manager._settings['Format']['Scripture']['HeaderFooter']['FooterContent'].get('runningFooterOddLeft', 'empty')
		runningFooterOddCenter = self._log_manager._settings['Format']['Scripture']['HeaderFooter']['FooterContent'].get('runningFooterOddCenter', 'empty')
		runningFooterOddRight = self._log_manager._settings['Format']['Scripture']['HeaderFooter']['FooterContent'].get('runningFooterOddRight', 'empty')
		runningFooterEvenLeft = self._log_manager._settings['Format']['Scripture']['HeaderFooter']['FooterContent'].get('runningFooterEvenLeft', 'empty')
		runningFooterEvenCenter = self._log_manager._settings['Format']['Scripture']['HeaderFooter']['FooterContent'].get('runningFooterEvenCenter', 'empty')
		runningFooterEvenRight = self._log_manager._settings['Format']['Scripture']['HeaderFooter']['FooterContent'].get('runningFooterEvenRight', 'empty')
		# Footnotes
		useAutoCallers = self._log_manager._settings['Format']['Scripture']['Footnotes'].get('useAutoCallers', '*')
		autoCallerCharFn = self._log_manager._settings['Format']['Scripture']['Footnotes'].get('autoCallerCharFn', '*')
		autoCallerCharCr = self._log_manager._settings['Format']['Scripture']['Footnotes'].get('autoCallerCharCr', '*')
		autoCallerStartChar = self._log_manager._settings['Format']['Scripture']['Footnotes'].get('autoCallerStartChar', '97')
		autoCallerNumChars = self._log_manager._settings['Format']['Scripture']['Footnotes'].get('autoCallerNumChars', '26')
		useNumericCallersFootnotes = self._log_manager._settings['Format']['Scripture']['Footnotes'].get('useNumericCallersFootnotes', 'false')
		useNumericCallersCrossRefs = self._log_manager._settings['Format']['Scripture']['Footnotes'].get('useNumericCallersCrossRefs', 'false')
		pageResetCallersFootnotes = self._log_manager._settings['Format']['Scripture']['Footnotes'].get('pageResetCallersFootnotes', 'false')
		pageResetCallersCrossRefs = self._log_manager._settings['Format']['Scripture']['Footnotes'].get('pageResetCallersCrossRefs', 'false')
		omitCallerInFootnote = self._log_manager._settings['Format']['Scripture']['Footnotes'].get('omitCallerInFootnote', 'false')
		omitCallerInCrossRefs = self._log_manager._settings['Format']['Scripture']['Footnotes'].get('omitCallerInCrossRefs', 'false')
		paragraphedFootnotes = self._log_manager._settings['Format']['Scripture']['Footnotes'].get('paragraphedFootnotes', 'false')
		paragraphedCrossRefs = self._log_manager._settings['Format']['Scripture']['Footnotes'].get('paragraphedCrossRefs', 'false')
		footnoteRule = self._log_manager._settings['Format']['Scripture']['Footnotes'].get('footnoteRule', 'true')
		justifyPars = self._log_manager._settings['Format']['Scripture']['TextElements'].get('justifyPars', 'true')
		rightToLeft = self._log_manager._settings['Format']['Scripture']['TextElements'].get('rightToLeft', 'false')

		# Build our output - These are the strings we will fill:
		fileHeaderText = ''
		fileInput = ''
		verseChapterSettings = ''
		headerSettings = ''
		footerSettings = ''
		footnoteSettings = ''
		generalSettings = ''

		# Set some context sensitive things here
		# Note that for now, we are going to put header and footer settings
		# only in the 'bible' context.
		if self._contextFlag.lower() == 'cover' :
			fileName = self._cvSettingsFile
			# There is not much to a cover file but we know that we
			# need to turn off all the header and footer output
			headerSettings = headerSettings + self.RemovePageNumbers(self._headerPositions)
			footerSettings = footerSettings + self.RemovePageNumbers(self._footerPositions)

		elif self._contextFlag.lower() == 'front' :
			fileName = self._fmSettingsFile
			headerSettings = headerSettings + self.RemovePageNumbers(self._headerPositions)
			footerSettings = footerSettings + self.RemovePageNumbers(self._footerPositions)

		elif self._contextFlag.lower() == 'back' :
			fileName = self._bmSettingsFile
			headerSettings = headerSettings + self.RemovePageNumbers(self._headerPositions)
			footerSettings = footerSettings + self.RemovePageNumbers(self._footerPositions)

		elif self._contextFlag.lower() == 'bible' :
			fileName = self._biSettingsFile
			# Path to Illustration files (what if we are not using them?)
			fileInput = fileInput + '\\PicPath={' + self._pathToIllustrations + '}\n'
			# Will we use marginal verses?
			if useMarginalVerses.lower() == 'true' :
				fileInput = fileInput + '\\input ' + marginalVersesMacro + '\n'
				fileInput = fileInput + '\\columnshift=' + columnshift + 'pt\n'
			# First off, if a file name for the TOC is found, write it out
			if generateTOC == 'true' :
				fileInput = fileInput + '\\GenerateTOC[' + tocTitle + ']{' + autoTocFile + '}\n'
			# Do we want a page border?
			if usePageBorder.lower() == 'true' :
				if pageBorderScale == '' :
					fileInput = fileInput + '\\def\\PageBorder{' + pageBorderFile + '}\n'
				else :
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
				verseChapterSettings = verseChapterSettings + '\\def\\AdornVerseNumber#1{(#1)}\n'
			verseChapterSettings = verseChapterSettings + '\\def\\ChapterVerseSeparator{' + chapterVerseSeparator + '}\n'
			verseChapterSettings = verseChapterSettings + '\\def\\AfterVerseSpaceFactor{' + afterVerseSpaceFactor + '}\n'
			verseChapterSettings = verseChapterSettings + '\\def\\AfterChapterSpaceFactor{' + afterChapterSpaceFactor + '}\n'
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
			if useAutoCallers == 'true' :
				footnoteSettings = footnoteSettings + '\\AutoCallers{f}{' + autoCallerCharFn + '}\n'
				footnoteSettings = footnoteSettings + '\\AutoCallers{x}{' + autoCallerCharCr + '}\n'
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
			if omitCallerInFootnote.lower() == 'true' :
				footnoteSettings = footnoteSettings + '\\OmitCallerInNote{f}\n'
			if omitCallerInCrossRefs.lower() == 'true' :
				footnoteSettings = footnoteSettings + '\\OmitCallerInNote{x}\n'
			if paragraphedFootnotes.lower() == 'true' :
				footnoteSettings = footnoteSettings + '\\ParagraphedNotes{f}\n'
			if paragraphedCrossRefs.lower() == 'true' :
				footnoteSettings = footnoteSettings + '\\ParagraphedNotes{x}\n'
			# General settings
			if useFigurePlaceholders.lower() == 'true' :
				generalSettings = generalSettings + '\\FigurePlaceholderstrue\n'

		else :
			# If we can't figure out what this is we have a system level bug and we might as well quite here
			self._log_manager.log("ERRR", "The context flag: " + self._contextFlag + " is not recognized by the system. Process halted.")
			return

		# The file header telling users not to touch it
		fileHeaderText = '% File: ' + fileName + '\n\n' + \
			'% This file is auto generated. If you know what is good for you, will not edit it!\n\n'

		# General settings
		if justifyPars.lower() == 'false' :
			generalSettings = generalSettings + '\\JustifyParsfalse\n'

		if rightToLeft.lower() == 'true' :
			generalSettings = generalSettings + '\\RTLtrue\n'

		# Ship the results, change order as needed
		orderedContents =     fileHeaderText + \
					fileInput + \
					verseChapterSettings + \
					headerSettings + \
					footerSettings + \
					footnoteSettings + \
					generalSettings + \
					'\n'

		self.writeOutTheFile(orderedContents)


#########################################################################################

	def RemovePageNumbers (self, positions) :
		'''This will simply return a list of page header or footer
			positions with \empty in them this takes out page
			numbers on peripheral matter pages.'''

		texCode = ''
		for place in positions :
			texCode = texCode + '\\def\\' + place + '{\\empty}\n'

		return texCode

	def writeOutTheFile (self, contents) :
		'''Write out the file.'''

		texControlObject = codecs.open(self._outputFile, "w", encoding='utf_8_sig')
		texControlObject.write(contents)
		texControlObject.close()
		self._log_manager.log("DBUG", "Wrote out the file: " + self._outputFile)

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


