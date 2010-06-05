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
		self._cvSettingsFile = log_manager._settings['Process']['Files'].get('FILE_TEX_COVER', '.cover_settings.txt')
		self._fmSettingsFile = log_manager._settings['Process']['Files'].get('FILE_TEX_FRONT', '.front_settings.txt')
		self._biSettingsFile = log_manager._settings['Process']['Files'].get('FILE_TEX_BIBLE', '.bible_settings.txt')
		self._bmSettingsFile = log_manager._settings['Process']['Files'].get('FILE_TEX_BACK', '.back_settings.txt')
		self._cmSettingsFile = os.getcwd() + "/" + log_manager._settings['Process']['Files'].get('FILE_TEX_CUSTOM', 'custom-tex.txt')
		self._txSettingsFile = log_manager._settings['Process']['Files'].get('FILE_TEX_SETUP', '.setup_tex.txt')
		# Note we get the value from the input file field
		self._contextFlag = log_manager._optionalPassedVariable
		self._flags = ('front', 'bible', 'back')
		self._frontMatter = log_manager._settings['Process']['Binding']['MATTER_FRONT'].split()
		self._backMatter = log_manager._settings['Process']['Binding']['MATTER_BACK'].split()
		self._publicationType = log_manager._publicationType
		self._pathToText = os.getcwd() + "/" + log_manager._settings['Process']['Paths'].get('PATH_TEXTS', 'Texts')

		if self._publicationType.lower() == 'scripture' :

			# Decide which file we are needing to make, then direct it to
			# the right function.
			if self._txSettingsFile == self._outputFile :
				# This is the project-wide setup file that contains
				# general project parameters
				self.makeTheSettingsFile()

			elif self._contextFlag in self._flags :
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

		# All local control files will link to the main settings file
		settings = '\\input ' + self._txSettingsFile + '\n'

		# Now link to the custom settings file. As this can override some
		# settings it seems that it would be best for it to come near the end
		# of the initialization process. The control file would be the best
		# place to bing it in.
		settings = settings + '\\input ' + self._cmSettingsFile + '\n'

		# Make a link to the local override stylesheet. This file can override
		# styles that were introduced in the main setup file
		settings = settings + '\\stylesheet{' + self._inputFile + '.sty}\n'

		# Being passed here means the contextFlag was not empty. That
		# being the case, it must be a scripture book. Otherwise, it is
		# a peripheral control file.
		if self._contextFlag != '' :

			settings = settings + '\\input ' + self._biSettingsFile + '\n'

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
				# The file(s) we need to point to in this instance are not
				# found in the inputFile, we have to generate them here.
				thisBook = self._pathToText + '/' + book.lower() + '.usfm'
				bookInfo = self.parseThisBook(thisBook)
				if oneChapOmmitRule == 'true' and bookInfo['chapCount'] == 1 or omitAllChapterNumbers == 'true':
					settings = settings + '\\OmitChapterNumbertrue\n'
					settings = settings + '\\ptxfile{' + thisBook + '}\n'
					settings = settings + '\\OmitChapterNumberfalse\n'
				else :
					settings = settings + '\\ptxfile{' + self._outputFile + '}\n'

		# If there was no context flag at all that means it has to be peripheral
		# matter. But is is front or back matter. we'll need to test to see
		else :
			if self._inputFile in self._frontMatter :
				settings = settings + '\\input ' + self._fmSettingsFile + '\n'

			elif self._inputFile in self._backMatter :
				settings = settings + '\\input ' + self._bmSettingsFile + '\n'

			else :
				self._log_manager.log("ERRR", "This module thinks that: " + self._inputFile + " part of the peripheral matter but it cannot find it on either the front or back matter binding lists. Process halted.")
				return

			# For peripheral matter we do not have to generate the name like
			# with Scripture books
			settings = settings + '\\ptxfile{' + self._inputFile + '}\n'

		# Ship the results, change order as needed
		self.writeOutTheFile(self._outputFile, settings + '\\bye\n')

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
		styleFile = os.getcwd() + "/" + log_manager._settings['Process']['Files'].get('FILE_TEX_STYLE', 'project.sty')
		# Bring in page format settings
		cropmarks = log_manager._settings['Format']['PageLayout'].get('CROPMARKS', 'true')
		pageHeight = log_manager._settings['Format']['PageLayout'].get('pageHeight', '210mm')
		pageWidth = log_manager._settings['Format']['PageLayout'].get('pageWidth', '148mm')
		endBookNoEject = log_manager._settings['Format']['Scripture']['Columns'].get('endBookNoEject', 'false')
		titleColumns = log_manager._settings['Format']['Scripture']['Columns'].get('titleColumns', '1')
		introColumns = log_manager._settings['Format']['Scripture']['Columns'].get('introColumns', '1')
		bodyColumns = log_manager._settings['Format']['Scripture']['Columns'].get('bodyColumns', '2')
		columnGutterFactor = log_manager._settings['Format']['Scripture']['Columns'].get('columnGutterFactor', '15')
		columnGutterRule = log_manager._settings['Format']['Scripture']['Columns'].get('columnGutterRule', 'false')
		columnGutterRuleSkip = log_manager._settings['Format']['Scripture']['Columns'].get('columnGutterRuleSkip', '4')
		# Margins
		marginUnit = log_manager._settings['Format']['Scripture']['Margins'].get('marginUnit', '12')
		topMarginFactor = log_manager._settings['Format']['Scripture']['Margins'].get('topMarginFactor', '1.0')
		bottomMarginFactor = log_manager._settings['Format']['Scripture']['Margins'].get('bottomMarginFactor', '0')
		sideMarginFactor = log_manager._settings['Format']['Scripture']['Margins'].get('sideMarginFactor', '0.7')
		useBindingGutter = log_manager._settings['Format']['Scripture']['Margins'].get('useBindingGutter', 'false')
		bindingGutter = log_manager._settings['Format']['Scripture']['Margins'].get('bindingGutter', '12')
		# Header/Footer
		headerPosition = log_manager._settings['Format']['Scripture']['HeaderFooter'].get('headerPosition', '0.5')
		footerPosition = log_manager._settings['Format']['Scripture']['HeaderFooter'].get('footerPosition', '0.5')
		# Fonts and text
		xetexLineBreakLocale = log_manager._settings['Format']['Fonts'].get('xetexLineBreakLocale', 'false')
		fontDefRegular = log_manager._settings['Format']['Fonts'].get('fontDefRegular', '[../Fonts/GenBkBas/GenBkBasR.ttf]/GR')
		fontDefBold = log_manager._settings['Format']['Fonts'].get('fontDefBold', '[../Fonts/GenBkBas/GenBkBasB.ttf]/GR')
		fontDefItalic = log_manager._settings['Format']['Fonts'].get('fontDefItalic', '[../Fonts/GenBkBas/GenBkBasI.ttf]/GR')
		fontDefBoldItalic = log_manager._settings['Format']['Fonts'].get('fontDefBoldItalic', '[../Fonts/GenBkBas/GenBkBasBI.ttf]/GR')
		tracingLostCharacters = log_manager._settings['Format']['Fonts'].get('tracingLostCharacters', 'false')
		fontSizeUnit = log_manager._settings['Format']['Fonts'].get('fontSizeUnit', '1')
		lineSpacingFactor = log_manager._settings['Format']['Fonts'].get('lineSpacingFactor', '1.1')
		verticalSpaceFactor = log_manager._settings['Format']['Fonts'].get('verticalSpaceFactor', '1')

		# Build our output - These are the strings we will fill:
		fileHeaderText = ''
		fileInput = ''
		formatSettings = ''
		headerFooterSettings = ''
		fontSettings = ''

		# Create the file header
		fileHeaderText =	"% tex_settings.txt\n\n% This is an auto-generated file, do not edit. Any necessary changes\n" + \
					"% should be made to the project.conf file or the custom TeX setup file.\n\n"
		# Make all the file input settings here
		fileInput = '\\input ' + texMacros + '\n'
		# Add the global style sheet
		fileInput = fileInput + '\\stylesheet{' + styleFile + '}\n'
		# Add format settings
		formatSettings + '\\PaperHeight=' + pageHeight + '\n'
		formatSettings = formatSettings + '\\PaperWidth=' + pageWidth + '\n'
		if cropmarks.lower() == 'true' :
			formatSettings = formatSettings + '\\CropMarkstrue\n'
		if endBookNoEject.lower() == 'true' :
			formatSettings = formatSettings + '\\endbooknoejecttrue\n'
		# Columns
		formatSettings = formatSettings + '\\TitleColumns=' + titleColumns + '\n'
		formatSettings = formatSettings + '\\IntroColumns=' + introColumns + '\n'
		formatSettings = formatSettings + '\\BodyColumns=' + bodyColumns + '\n'
		formatSettings = formatSettings + '\\def\ColumnGutterFactor{' + columnGutterFactor + '}\n'
		if columnGutterRule.lower() == 'true' :
			formatSettings = formatSettings + '\\ColumnGutterRuletrue\n'
		formatSettings = formatSettings + '\\ColumnGutterRuleSkip=' + columnGutterRuleSkip + '\n'
		# Margins
		formatSettings = formatSettings + '\\MarginUnit=' + marginUnit + '\n'
		formatSettings = formatSettings + '\\def\TopMarginFactor{' + topMarginFactor + '}\n'
		formatSettings = formatSettings + '\\def\BottomMarginFactor{' + bottomMarginFactor + '}\n'
		formatSettings = formatSettings + '\\def\SideMarginFactor{' + sideMarginFactor + '}\n'
		formatSettings = formatSettings + '\\BindingGutter=' + bindingGutter + '}\n'
		if useBindingGutter.lower() == 'true' :
			formatSettings = formatSettings + '\\BindingGuttertrue\n'
		# HeaderFooter
		headerFooterSettings = headerFooterSettings + '\\def\HeaderPosition{' + headerPosition + '}\n'
		headerFooterSettings = headerFooterSettings + '\\def\FooterPosition{' + footerPosition + '}\n'
		# Fonts
		if xetexLineBreakLocale.lower() == 'true' :
			fontSettings = fontSettings + '\\XeTeXlinebreaklocale "G"\n'
		fontSettings = fontSettings + '\\def\regular{' + fontDefRegular + '}\n'
		fontSettings = fontSettings + '\\def\bold{' + fontDefBold + '}\n'
		fontSettings = fontSettings + '\\def\italic{' + fontDefItalic + '}\n'
		fontSettings = fontSettings + '\\def\bolditalic{' + fontDefBoldItalic + '}\n'
		if tracingLostCharacters.lower() == 'true' :
			fontSettings = fontSettings + '\\tracinglostchars=1\n'
		fontSettings = fontSettings + '\\FontSizeUnit=' + fontSizeUnit + '\n'
		fontSettings = fontSettings + '\\def\LineSpacingFactor{' + lineSpacingFactor + '}\n'
		fontSettings = fontSettings + '\\def\VerticalSpaceFactor{' + verticalSpaceFactor + '}\n'

		# Ship the results, change order as needed
		orderedContents = 	fileHeaderText + \
					fileInput + \
					formatSettings + \
					headerFooterSettings + \
					fontSettings + \
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
		pathToHyphen = os.getcwd() + "/" + log_manager._settings['Process']['Paths'].get('PATH_HYPHENATION', 'Hyphenation')
		pathToIllustrations = os.getcwd() + "/" + log_manager._settings['Process']['Paths'].get('PATH_ILLUSTRATIONS', 'Illustrations')
		hyphenFile = pathToHyphen + "/" + log_manager._settings['Process']['Files'].get('FILE_HYPHENATION_TEX', '')
		marginalVerses = log_manager._settings['Process']['Files'].get('FILE_MARGINAL_VERSES', 'ptxplus-marginalverses.tex')
		useHyphenation = log_manager._settings['Process']['Hyphenation'].get('useHyphenation', 'true')
		useFigurePlaceholders = log_manager._settings['Format']['Scripture']['Illustrations'].get('useFigurePlaceholders', 'true')
		autoTocFile = log_manager._settings['Process']['Paths'].get('FILE_AUTO_TOC', 'auto-toc')
		generateTOC = log_manager._settings['Process']['TOC'].get('generateTOC', 'true')
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
		elif self._contextFlag.lower() == 'front' :
			fileName = self._fmSettingsFile
		elif self._contextFlag.lower() == 'bible' :
			fileName = self._biSettingsFile
			# Will we use marginal verses?
			if useMarginalVerses.lower() == 'true' :
				fileInput = fileInput + '\\input ' + marginalVerses + '\n'
				fileInput = fileInput + '\\columnshift=' + columnshift + '\n'
			# First off, if a file name for the TOC is found, write it out
			if generateTOC == 'true' :
				fileInput = fileInput + '\\GenerateTOC[' + tocTitle + ']{' + autoTocFile + '}\n'
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
			# Hyphenation is optional project-wide so we will put it here. However, this
			# means there will not be any hyphenation on any non-Scripture objects. We might
			# need to rethink this.
			if useHyphenation.lower() == 'true' :
				fileInput = fileInput + '\\input ' + hyphenFile + '\n'
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


		elif self._contextFlag.lower == 'back' :
			fileName = self._bmSettingsFile
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
		orderedContents = 	fileHeaderText + \
					fileInput + \
					verseChapterSettings + \
					headerSettings + \
					footerSettings + \
					footnoteSettings + \
					generalSettings + \
					'\\bye\n'

		self.writeOutTheFile(orderedContents)


#########################################################################################

	def writeOutTheFile (self, contents) :
		'''Write out the file.'''

		texControlObject = codecs.open(self._outputFile, "w", encoding='utf_8_sig')
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
