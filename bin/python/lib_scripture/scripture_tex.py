#!/usr/bin/python2
# -*- coding: utf_8 -*-
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
# 20100630 - djd - Combine the main settings file with the
#       Bible settings file


#############################################################
######################### Shell Class #######################
#############################################################

import codecs, os
import parse_sfm

# Import supporting local classes
from encoding_manager import *
import tools


class MakeTexControlFile (object) :

	def main (self, log_manager) :
		'''This part is all about direction. In this function we will figure out
			what kind of settings file needs to be made and then call the
			right function to do it.'''

		log_manager._currentSubProcess  = 'MkTexContFile'
		self._log_manager               = log_manager
		self._inputFile                 = log_manager._currentInput
		self._outputFile                = log_manager._currentOutput
		self._inputID                   = log_manager._currentTargetID
		self._pathToText                = os.getcwd() + "/" + tools.pubInfoObject['Paths']['PATH_TEXTS']
		self._pathToSource              = os.path.abspath(self._log_manager._settings['System']['Paths']['PATH_SOURCE'])
		self._pathToIllustrations       = os.path.abspath(self._log_manager._settings['System']['Paths']['PATH_ILLUSTRATIONS'])
		self._pathToProcess             = os.getcwd() + "/" + tools.pubInfoObject['Paths']['PATH_PROCESS']
		self._texMacros                 = tools.pubInfoObject['Files']['FILE_TEX_MACRO']
		self._cvSettingsFile            = self._pathToProcess + "/" + tools.pubInfoObject['Files']['FILE_TEX_COVER']
		self._fmSettingsFile            = self._pathToProcess + "/" + tools.pubInfoObject['Files']['FILE_TEX_FRONT']
		self._bmSettingsFile            = self._pathToProcess + "/" + tools.pubInfoObject['Files']['FILE_TEX_BACK']
#        self._mpSettingsFile            = self._pathToProcess + "/" + tools.pubInfoObject['Files']['FILE_TEX_MAPS']
		self._cmSettingsFile            = self._pathToProcess + "/" + tools.pubInfoObject['Files']['FILE_TEX_CUSTOM']
		self._biSettingsFile            = self._pathToProcess + "/" + tools.pubInfoObject['Files']['FILE_TEX_SETTINGS']
		self._bibleStyleFile            = self._pathToProcess + '/' + tools.pubInfoObject['Files']['FILE_TEX_STYLE']
		self._mapStyleFile              = self._pathToProcess + '/' + tools.pubInfoObject['Files']['FILE_GROUP_MAPS_STY']
		# Note we get the value from the input file field
		self._contextFlag               = log_manager._optionalPassedVariable
		self._flags                     = ('cover', 'front', 'back', 'periph', 'maps')
		self._frontMatter               = self._log_manager._settings['Format']['BindingGroups']['GROUP_FRONT']
		self._backMatter                = self._log_manager._settings['Format']['BindingGroups']['GROUP_BACK']
		self._coverMatter               = self._log_manager._settings['Format']['BindingGroups']['GROUP_COVER']
		self._contentMatter             = self._log_manager._settings['Format']['BindingGroups']['GROUP_CONTENT']
		self._mapMatter                 = self._log_manager._settings['Format']['BindingGroups']['GROUP_MAPS']
		self._contentGroup              = []
		self._contentGroup.extend(self._contentMatter)
		self._publicationType           = log_manager._publicationType
		# File extentions (Expand this, more will be needed in the future)
		self._extStyle                  = tools.pubInfoObject['Extensions']['EXT_STYLE']
		self._extWork                   = tools.pubInfoObject['Extensions']['EXT_WORK']
		self._extPDF                    = tools.pubInfoObject['Extensions']['EXT_PDF']
		# Some lists
		self._headerPositions           = ['RHtitleleft', 'RHtitlecenter', 'RHtitleright', \
											'RHoddleft', 'RHoddcenter', 'RHoddright', \
											'RHevenleft', 'RHevencenter', 'RHevenright']
		self._footerPositions           = ['RFtitleleft', 'RFtitlecenter', 'RFtitleright', \
											'RFoddleft', 'RFoddcenter', 'RFoddright', \
											'RFevenleft', 'RFevencenter', 'RFevenright']
		# Some global settings
		self._useMarginalVerses         = self._log_manager._settings['Format']['ChapterVerse']['useMarginalVerses']

		# Direct to the right context
		if self._publicationType.lower() == 'scripture' :
			# Decide which file we are needing to make, then direct it to
			# the right function. (Assume the file name has the path in it.)
			if self._biSettingsFile.split('/')[-1] in self._outputFile.split('/') :
				# This is the project-wide setup file that contains
				# general project parameters. The file name tells us
				# where to go.
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
		oneChapOmmitRule = self._log_manager._settings['Format']['ChapterVerse']['shortBookChapterOmit']
		omitAllChapterNumbers = self._log_manager._settings['Format']['ChapterVerse']['omitAllChapterNumbers']
		useHyphenation = self._log_manager._settings['Format']['Hyphenation']['useHyphenation']
		pathToHyphen = os.getcwd() + "/" + tools.pubInfoObject['Paths']['PATH_HYPHENATION']
		hyphenFile = pathToHyphen + "/" + tools.pubInfoObject['Files']['FILE_HYPHENATION_TEX']
		generateTOC = self._log_manager._settings['Format']['TOC']['generateTOC']
		marginalVersesMacro = tools.pubInfoObject['Files']['FILE_MARGINAL_VERSES']

		# TOC Process
		autoTocFile = tools.pubInfoObject['Files']['FILE_TOC_AUTO']
		tocTitle = self._log_manager._settings['Format']['TOC']['mainTitle']

		# Input the main macro set here in the control file
		settings = '\\input \"' + self._texMacros + '\"\n'

		# All local control files will link to the main settings file
		settings += '\\input \"' + self._biSettingsFile + '\"\n'

		# Now link to the custom settings file. As this can override some
		# settings it seems that it would be best for it to come near the end
		# of the initialization process. The control file would be the best
		# place to bing it in.
		settings += '\\input \"' + self._cmSettingsFile + '\"\n'

		# If there is no ID given then this is probably peripheral stuff
		# which means we need to output general peripheral TeX settings
		# file input for what ever kind of peripheral matter it is.
		if self._inputID == '' :
			if self._inputFile.split('/')[-1] in self._frontMatter :
				settings += '\\input \"' + self._fmSettingsFile + '\"\n'

			elif self._inputFile.split('/')[-1] in self._backMatter :
				settings += '\\input \"' + self._bmSettingsFile + '\"\n'

			elif self._inputFile.split('/')[-1] in self._coverMatter :
				settings += '\\input \"' + self._cvSettingsFile + '\"\n'

			# Note: this is not done for map matter

			else :
				self._log_manager.log("ERRR", "Trying to Create: " + self._outputFile + " - This module thinks that input: [" + self._inputFile + "] is part of the peripheral matter but it cannot find it on either the cover, front or back matter binding groups. Process halted.")
				return

		# Add the global style sheet
		settings += '\\stylesheet{' + self._bibleStyleFile + '}\n'

		# Being passed here means the contextFlag was not empty. That
		# being the case, it must be a scripture book. Otherwise, it is
		# a peripheral control file.
		if self._inputID != '' :

			# Hyphenation is optional project-wide so we will put it here. However,
			# we might need to rethink this.
			if useHyphenation.lower() == 'true' :
				settings += '\\input \"' + hyphenFile + '\"\n'

			# Are we using marginal verses?
			# Really, we don't want to put this here but due to a problem with
			# passing style params, we need to pull in the marginal verse macro
			# code at this point.
			if self._useMarginalVerses.lower() == 'true' :
				settings += '\\input \"' + marginalVersesMacro + '\"\n'

			# Since we were passed here it is assmumed that the context
			# flag will contain a book ID, or will represent the entire
			# content group.
			# If it isn't the content group, then we assume it is a
			# single book and we will only process that one book based
			# on the book ID given.
			# And while we are at it, we'll generate a TOC file if this
			# is for the content group.
			componentScripture = []
			if self._inputID == 'content' :
				componentScripture = self._contentGroup
				if generateTOC == 'true' :
					settings += '\\GenerateTOC[' + tocTitle + ']{' + autoTocFile + '}\n'
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
				thisBook = self._pathToText + '/' + book.lower() + '.' + self._extWork
				bookInfo = self.parseThisBook(thisBook)
				if (oneChapOmmitRule == 'true' and bookInfo['chapCount'] == 1) or omitAllChapterNumbers == 'true' :
					settings += '\\OmitChapterNumbertrue\n'
					settings += '\\ptxfile{' + thisBook + '}\n'
					settings += '\\OmitChapterNumberfalse\n'
				else :
					settings += '\\ptxfile{' + thisBook + '}\n'

		# If there was no context flag at all that means it has to be peripheral
		# matter. But is is front or back matter. we'll need to test to see
		else :
			# Make a link to the custom override style sheet for peripheral material.
			settings += '\\stylesheet{' + self._pathToProcess + "/" + self._inputFile + '.' + self._extStyle + '}\n'

			# For peripheral matter we do not have to generate the name like
			# with Scripture books
			settings += '\\ptxfile{' + self._pathToText + '/' + self._inputFile + '.' + self._extWork + '}\n'

		# Combine the results
		settings += '\\bye\n'

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

		# Bring in page format settings
		useCropmarks = self._log_manager._settings['Format']['PageLayout']['USE_CROPMARKS']
		pageHeight = self._log_manager._settings['Format']['PageLayout']['pageHeight']
		pageWidth = self._log_manager._settings['Format']['PageLayout']['pageWidth']
		endBookNoEject = self._log_manager._settings['Format']['PageLayout']['endBookNoEject']
		titleColumns = self._log_manager._settings['Format']['Columns']['titleColumns']
		introColumns = self._log_manager._settings['Format']['Columns']['introColumns']
		bodyColumns = self._log_manager._settings['Format']['Columns']['bodyColumns']
		columnGutterFactor = self._log_manager._settings['Format']['Columns']['columnGutterFactor']
		columnGutterRule = self._log_manager._settings['Format']['Columns']['columnGutterRule']
		columnGutterRuleSkip = self._log_manager._settings['Format']['Columns']['columnGutterRuleSkip']
		columnshift = self._log_manager._settings['Format']['Columns']['columnshift']

		# Format -> PageLayout
		useFigurePlaceholders = self._log_manager._settings['Format']['Illustrations']['USE_PLACEHOLDERS']
		useIllustrations = self._log_manager._settings['Format']['Illustrations']['USE_ILLUSTRATIONS']
		usePageBorder = self._log_manager._settings['Format']['PageLayout']['USE_PAGE_BORDER']
		pageBorderScale = self._log_manager._settings['Format']['PageLayout']['pageBorderScale']
		pageBorderFile = self._log_manager._settings['Format']['PageLayout']['FILE_PAGE_BORDER']

		# Format -> Scripture
		useRunningHeaderRule = self._log_manager._settings['Format']['HeaderFooter']['useRunningHeaderRule']
		runningHeaderRulePosition = self._log_manager._settings['Format']['HeaderFooter']['runningHeaderRulePosition']
		verseRefs = self._log_manager._settings['Format']['HeaderFooter']['HeaderContent']['verseRefs']
		omitBookRef = self._log_manager._settings['Format']['HeaderFooter']['HeaderContent']['omitBookRef']
		chapterVerseSeparator = self._log_manager._settings['Format']['ChapterVerse']['chapterVerseSeparator']
		omitChapterNumber = self._log_manager._settings['Format']['ChapterVerse']['omitAllChapterNumbers']
		omitVerseNumberOne = self._log_manager._settings['Format']['ChapterVerse']['omitVerseNumberOne']
		afterVerseSpaceFactor = self._log_manager._settings['Format']['ChapterVerse']['afterVerseSpaceFactor']
		afterChapterSpaceFactor = self._log_manager._settings['Format']['ChapterVerse']['afterChapterSpaceFactor']
		removeIndentAfterHeading = self._log_manager._settings['Format']['ChapterVerse']['removeIndentAfterHeading']
		adornVerseNumber = self._log_manager._settings['Format']['ChapterVerse']['adornVerseNumber']
		verseMarker = self._log_manager._settings['Format']['ChapterVerse']['verseMarker']

		# Running Header
		runningHeaderTitleLeft = self._log_manager._settings['Format']['HeaderFooter']['HeaderContent']['runningHeaderTitleLeft']
		runningHeaderTitleCenter = self._log_manager._settings['Format']['HeaderFooter']['HeaderContent']['runningHeaderTitleCenter']
		runningHeaderTitleRight = self._log_manager._settings['Format']['HeaderFooter']['HeaderContent']['runningHeaderTitleRight']
		runningHeaderOddLeft = self._log_manager._settings['Format']['HeaderFooter']['HeaderContent']['runningHeaderOddLeft']
		runningHeaderOddCenter = self._log_manager._settings['Format']['HeaderFooter']['HeaderContent']['runningHeaderOddCenter']
		runningHeaderOddRight = self._log_manager._settings['Format']['HeaderFooter']['HeaderContent']['runningHeaderOddRight']
		runningHeaderEvenLeft = self._log_manager._settings['Format']['HeaderFooter']['HeaderContent']['runningHeaderEvenLeft']
		runningHeaderOddCenter = self._log_manager._settings['Format']['HeaderFooter']['HeaderContent']['runningHeaderOddCenter']
		runningHeaderEvenRight = self._log_manager._settings['Format']['HeaderFooter']['HeaderContent']['runningHeaderEvenRight']
		runningFooterTitleLeft = self._log_manager._settings['Format']['HeaderFooter']['FooterContent']['runningFooterTitleLeft']
		runningFooterTitleCenter = self._log_manager._settings['Format']['HeaderFooter']['FooterContent']['runningFooterTitleCenter']
		runningFooterTitleRight = self._log_manager._settings['Format']['HeaderFooter']['FooterContent']['runningFooterTitleRight']
		runningFooterOddLeft = self._log_manager._settings['Format']['HeaderFooter']['FooterContent']['runningFooterOddLeft']
		runningFooterOddCenter = self._log_manager._settings['Format']['HeaderFooter']['FooterContent']['runningFooterOddCenter']
		runningFooterOddRight = self._log_manager._settings['Format']['HeaderFooter']['FooterContent']['runningFooterOddRight']
		runningFooterEvenLeft = self._log_manager._settings['Format']['HeaderFooter']['FooterContent']['runningFooterEvenLeft']
		runningFooterEvenCenter = self._log_manager._settings['Format']['HeaderFooter']['FooterContent']['runningFooterEvenCenter']
		runningFooterEvenRight = self._log_manager._settings['Format']['HeaderFooter']['FooterContent']['runningFooterEvenRight']

		# Footnotes
		useAutoCallers              = self._log_manager._settings['Format']['Footnotes']['useAutoCallers']
		autoCallerCharFn            = self._log_manager._settings['Format']['Footnotes']['autoCallerCharFn']
		autoCallerCharCr            = self._log_manager._settings['Format']['Footnotes']['autoCallerCharCr']
		autoCallerStartChar         = self._log_manager._settings['Format']['Footnotes']['autoCallerStartChar']
		autoCallerNumChars          = self._log_manager._settings['Format']['Footnotes']['autoCallerNumChars']
		useNumericCallersFootnotes  = self._log_manager._settings['Format']['Footnotes']['useNumericCallersFootnotes']
		useNumericCallersCrossRefs  = self._log_manager._settings['Format']['Footnotes']['useNumericCallersCrossRefs']
		pageResetCallersFootnotes   = self._log_manager._settings['Format']['Footnotes']['pageResetCallersFootnotes']
		pageResetCallersCrossRefs   = self._log_manager._settings['Format']['Footnotes']['pageResetCallersCrossRefs']
		omitCallerInFootnote        = self._log_manager._settings['Format']['Footnotes']['omitCallerInFootnote']
		omitCallerInCrossRefs       = self._log_manager._settings['Format']['Footnotes']['omitCallerInCrossRefs']
		paragraphedFootnotes        = self._log_manager._settings['Format']['Footnotes']['paragraphedFootnotes']
		paragraphedCrossRefs        = self._log_manager._settings['Format']['Footnotes']['paragraphedCrossRefs']
		useFootnoteRule             = self._log_manager._settings['Format']['Footnotes']['useFootnoteRule']
		defineNewFootnoteRule       = self._log_manager._settings['Format']['Footnotes']['defineNewFootnoteRule']

		# Margins
		marginUnit                  = self._log_manager._settings['Format']['Margins']['marginUnit']
		topMarginFactor             = self._log_manager._settings['Format']['Margins']['topMarginFactor']
		bottomMarginFactor          = self._log_manager._settings['Format']['Margins']['bottomMarginFactor']
		sideMarginFactor            = self._log_manager._settings['Format']['Margins']['sideMarginFactor']
		useBindingGutter            = self._log_manager._settings['Format']['Margins']['useBindingGutter']
		extraRightMargin            = self._log_manager._settings['Format']['Margins']['extraRightMargin']
		bindingGutter               = self._log_manager._settings['Format']['Margins']['bindingGutter']

		# Header/Footer
		headerPosition              = self._log_manager._settings['Format']['HeaderFooter']['headerPosition']
		footerPosition              = self._log_manager._settings['Format']['HeaderFooter']['footerPosition']

		# Fonts and text
		xetexLineBreakLocale = self._log_manager._settings['Format']['Fonts']['xetexLineBreakLocale']
		fontDefRegular = self._log_manager._settings['Format']['Fonts']['fontDefRegular']
		fontDefBold = self._log_manager._settings['Format']['Fonts']['fontDefBold']
		fontDefItalic = self._log_manager._settings['Format']['Fonts']['fontDefItalic']
		fontDefBoldItalic = self._log_manager._settings['Format']['Fonts']['fontDefBoldItalic']
		tracingLostCharacters = self._log_manager._settings['Format']['Fonts']['tracingLostCharacters']
		fontSizeUnit = self._log_manager._settings['Format']['Fonts']['fontSizeUnit']
		lineSpacingFactor = self._log_manager._settings['Format']['Fonts']['lineSpacingFactor']
		verticalSpaceFactor = self._log_manager._settings['Format']['Fonts']['verticalSpaceFactor']

		# Build our output - These are the strings we will fill:
		fileHeaderText = ''
		fileInput = ''
		formatSettings = ''
		verseChapterSettings = ''
		headerFooterSettings = ''
		footnoteSettings = ''
		fontSettings = ''
		generalSettings = ''

		# Create the file header
		fileHeaderText +=    "% tex_settings.txt\n\n% This is an auto-generated file, do not edit. Any necessary changes\n" + \
					"% should be made to the project.conf file or the custom TeX setup file.\n\n"
		# Add format settings
		formatSettings += '\\PaperHeight=' + pageHeight + 'mm\n'
		formatSettings += '\\PaperWidth=' + pageWidth + 'mm\n'
		if useCropmarks.lower() == 'true' :
			formatSettings += '\\CropMarkstrue\n'
		if endBookNoEject.lower() == 'true' :
			formatSettings += '\\endbooknoejecttrue\n'
		# Columns
		formatSettings += '\\TitleColumns=' + titleColumns + '\n'
		formatSettings += '\\IntroColumns=' + introColumns + '\n'
		formatSettings += '\\BodyColumns=' + bodyColumns + '\n'
		formatSettings += '\\def\\ColumnGutterFactor{' + columnGutterFactor + '}\n'
		if columnGutterRule.lower() == 'true' :
			formatSettings += '\\ColumnGutterRuletrue\n'
		formatSettings += '\\ColumnGutterRuleSkip=' + columnGutterRuleSkip + 'mm\n'

		# Margins
		formatSettings += '\\MarginUnit=' + marginUnit + 'mm\n'
		formatSettings += '\\def\\TopMarginFactor{' + topMarginFactor + '}\n'
		formatSettings += '\\def\\BottomMarginFactor{' + bottomMarginFactor + '}\n'
		formatSettings += '\\def\\SideMarginFactor{' + sideMarginFactor + '}\n'
		formatSettings += '\\def\\ExtraRMargin=' + extraRightMargin + 'mm\n'
		if useBindingGutter.lower() == 'true' :
			formatSettings += '\\BindingGuttertrue\n'
			formatSettings += '\\BindingGutter=' + bindingGutter + 'mm\n'

		# Fonts
		if xetexLineBreakLocale.lower() == 'true' :
			fontSettings += '\\XeTeXlinebreaklocale \"G\"\n'
		fontSettings += '\\def\\regular{\"' + fontDefRegular + '\"}\n'
		fontSettings += '\\def\\bold{\"' + fontDefBold + '\"}\n'
		fontSettings += '\\def\\italic{\"' + fontDefItalic + '\"}\n'
		fontSettings += '\\def\\bolditalic{\"' + fontDefBoldItalic + '\"}\n'
		if tracingLostCharacters.lower() == 'true' :
			fontSettings += '\\tracinglostchars=1\n'
		fontSettings += '\\FontSizeUnit=' + fontSizeUnit + 'pt\n'
		fontSettings += '\\def\\LineSpacingFactor{' + lineSpacingFactor + '}\n'
		fontSettings += '\\def\\VerticalSpaceFactor{' + verticalSpaceFactor + '}\n'

		# Path to Illustration files (Note we add a "/" at the end so ptx2pdf can get it right.)
		if useIllustrations.lower() == 'true' :
			fileInput += '\\PicPath={' + self._pathToIllustrations + '/}\n'
		# Will we use marginal verses? This setting is
		# mainly for use with marginal verses
		if self._useMarginalVerses.lower() == 'true' :
			fileInput += '\\columnshift=' + columnshift + 'mm\n'
		# Do we want a page border?
		if usePageBorder.lower() == 'true' :
			if pageBorderScale == '' :
				fileInput += '\\def\\PageBorder{' + pageBorderFile + '}\n'
			else :
				fileInput += '\\def\\PageBorder{' + pageBorderFile + ' scaled ' + pageBorderScale + '}\n'

		# Verse/chapter settings
		if verseRefs.lower() == 'true' :
			verseChapterSettings += '\\VerseRefstrue\n'
		if omitChapterNumber.lower() == 'true' :
			verseChapterSettings += '\\OmitChapterNumberRHtrue\n'
		if omitBookRef.lower() == 'true' :
			verseChapterSettings += '\\OmitBookReftrue\n'
		if omitVerseNumberOne.lower() == 'true' :
			verseChapterSettings += '\\OmitVerseNumberOnetrue\n'
		if removeIndentAfterHeading.lower() == 'true' :
			verseChapterSettings += '\\IndentAfterHeadingtrue\n'
		if adornVerseNumber.lower() == 'true' :
			verseChapterSettings += '\\def\\AdornVerseNumber#1{(#1)}\n'
		verseChapterSettings += '\\def\\VerseMarker{' + verseMarker + '}\n'
		verseChapterSettings += '\\def\\ChapterVerseSeparator{' + chapterVerseSeparator + '}\n'
		verseChapterSettings += '\\def\\AfterVerseSpaceFactor{' + afterVerseSpaceFactor + '}\n'
		verseChapterSettings += '\\def\\AfterChapterSpaceFactor{' + afterChapterSpaceFactor + '}\n'

		# HeaderFooter
		headerFooterSettings += '\\def\\HeaderPosition{' + headerPosition + '}\n'
		headerFooterSettings += '\\def\\FooterPosition{' + footerPosition + '}\n'
		if useRunningHeaderRule.lower() == 'true' :
			headerFooterSettings += '\\RHruleposition=' + runningHeaderRulePosition + '\n'
		headerFooterSettings += '\\def\\RHtitleleft{\\' + runningHeaderTitleLeft + '}\n'
		headerFooterSettings += '\\def\\RHtitlecenter{\\' + runningHeaderTitleCenter + '}\n'
		headerFooterSettings += '\\def\\RHtitleright{\\' + runningHeaderTitleRight + '}\n'
		headerFooterSettings += '\\def\\RHoddleft{\\' + runningHeaderOddLeft + '}\n'
		headerFooterSettings += '\\def\\RHoddcenter{\\' + runningHeaderOddCenter + '}\n'
		headerFooterSettings += '\\def\\RHoddright{\\' + runningHeaderOddRight + '}\n'
		headerFooterSettings += '\\def\\RHevenleft{\\' + runningHeaderEvenLeft + '}\n'
		headerFooterSettings += '\\def\\RHevencenter{\\' + runningHeaderOddCenter + '}\n'
		headerFooterSettings += '\\def\\RHevenright{\\' + runningHeaderEvenRight + '}\n'

		# Footer settings
		headerFooterSettings += '\\def\\RFtitleleft{\\' + runningFooterTitleLeft + '}\n'
		headerFooterSettings += '\\def\\RFtitlecenter{\\' + runningFooterTitleCenter + '}\n'
		headerFooterSettings += '\\def\\RFtitleright{\\' + runningFooterTitleRight + '}\n'
		headerFooterSettings += '\\def\\RFoddleft{\\' + runningFooterOddLeft + '}\n'
		headerFooterSettings += '\\def\\RFoddcenter{\\' + runningFooterOddCenter + '}\n'
		headerFooterSettings += '\\def\\RFoddright{\\' + runningFooterOddRight + '}\n'
		headerFooterSettings += '\\def\\RFevenleft{\\' + runningFooterEvenLeft + '}\n'
		headerFooterSettings += '\\def\\RFevencenter{\\' + runningFooterEvenCenter + '}\n'
		headerFooterSettings += '\\def\\RFevenright{\\' + runningFooterEvenRight + '}\n'

		# Footnote settings
		# If we use Autocallers we need to leave out some other things and vise versa
		if useAutoCallers == 'true' :
			footnoteSettings += '\\AutoCallers{f}{' + autoCallerCharFn + '}\n'
			footnoteSettings += '\\AutoCallers{x}{' + autoCallerCharCr + '}\n'
		else :
			footnoteSettings += '\\def\\AutoCallerStartChar{' + autoCallerStartChar + '}\n'
			footnoteSettings += '\\def\\AutoCallerNumChars{' + autoCallerNumChars + '}\n'
			if useNumericCallersFootnotes.lower() == 'true' :
				footnoteSettings += '\\NumericCallers{f}\n'
			if useNumericCallersCrossRefs.lower() == 'true' :
				footnoteSettings += '\\NumericCallers{x}\n'
			if pageResetCallersFootnotes.lower() == 'true' :
				footnoteSettings += '\\PageResetCallers{f}\n'
			if pageResetCallersCrossRefs.lower() == 'true' :
				footnoteSettings += '\\PageResetCallers{x}\n'
		# This seems to be an inconsistancy in ptxplus. If the footnoterule
		# param is blank it will not put out anything. If it is not defined
		# at all it will put out the default 4pt hrule. This hopefully makes
		# it simpler to understand by the user.
		if useFootnoteRule.lower() == 'true' :
			if defineNewFootnoteRule != '' :
				footnoteSettings += '\\def\\footnoterule{' + defineNewFootnoteRule + '}\n'
			# The unstated else here is that if the user wants a footnote rule
			# but did not define anything, the default is used.
		else :
			# In this case the footnote rule is turned off by defining the
			# footnoterule to nothing

			footnoteSettings += '\\def\\footnoterule{}\n'
		if omitCallerInFootnote.lower() == 'true' :
			footnoteSettings += '\\OmitCallerInNote{f}\n'
		if omitCallerInCrossRefs.lower() == 'true' :
			footnoteSettings += '\\OmitCallerInNote{x}\n'
		if paragraphedFootnotes.lower() == 'true' :
			footnoteSettings += '\\ParagraphedNotes{f}\n'
		if paragraphedCrossRefs.lower() == 'true' :
			footnoteSettings += '\\ParagraphedNotes{x}\n'

		# General settings
		if useFigurePlaceholders.lower() == 'true' :
			generalSettings += '\\FigurePlaceholderstrue\n'
		# Allow the use of digets in text
		generalSettings += '\\catcode`@=11\n\\def\\makedigitsother{\\m@kedigitsother}\n\\def\\makedigitsletters{\\m@kedigitsletters}\n\\catcode `@=12\n'


		# Ship the results, change order as needed
		orderedContents =     fileHeaderText + \
					formatSettings + \
					headerFooterSettings + \
					fontSettings + \
					fileInput + \
					verseChapterSettings + \
					footnoteSettings + \
					generalSettings + \
					'\n'

		self.writeOutTheFile(orderedContents)


#########################################################################################

	def makeTheContextSettingsFile (self) :
		'''For each context that we render text in we need to tell TeX
			what the settings are for that context. This is a context
			sensitive settings file output routine.'''

		# Bring in settings we need
		justifyPars = self._log_manager._settings['Format']['TextElements']['justifyPars']
		rightToLeft = self._log_manager._settings['Format']['TextElements']['rightToLeft']

		# Build our output - These are the strings we will fill:
		macroSettings = ''
		fileHeaderText = ''
		formatSettings = ''
		headerSettings = ''
		footerSettings = ''
		generalSettings = ''
		mapSettings = ''

		# Set some context sensitive things here
		# Note that for now, we are going to put header and footer settings
		# only in the 'bible' context.
		if self._contextFlag.lower() == 'cover' :
			fileName = self._cvSettingsFile
			# There is not much to a cover file but we know that we
			# need to turn off all the header and footer output
			formatSettings += '\\TitleColumns=1\n'
			formatSettings += '\\IntroColumns=1\n'
			formatSettings += '\\BodyColumns=1\n'
			headerSettings += self.RemovePageNumbers(self._headerPositions)
			footerSettings += self.RemovePageNumbers(self._footerPositions)

		elif self._contextFlag.lower() == 'front' :
			fileName = self._fmSettingsFile
			formatSettings += '\\TitleColumns=1\n'
			formatSettings += '\\IntroColumns=1\n'
			formatSettings += '\\BodyColumns=1\n'
			headerSettings += self.RemovePageNumbers(self._headerPositions)
			footerSettings += self.RemovePageNumbers(self._footerPositions)

		elif self._contextFlag.lower() == 'back' :
			fileName = self._bmSettingsFile
			formatSettings += '\\TitleColumns=1\n'
			formatSettings += '\\IntroColumns=1\n'
			formatSettings += '\\BodyColumns=1\n'
			headerSettings += self.RemovePageNumbers(self._headerPositions)
			footerSettings += self.RemovePageNumbers(self._footerPositions)

		# Maps are a very different process from other types of matter.
		# The output here will be very different from the others.
		elif self._contextFlag.lower() == 'maps' :
			fileName = self._outputFile
			macroSettings += '\\input \"' + self._texMacros + '\"\n'
			macroSettings += '\\input \"' + self._biSettingsFile + '\"\n'
			macroSettings += '\\input \"' + self._cmSettingsFile + '\"\n'
			macroSettings += '\\stylesheet{' + self._bibleStyleFile + '}\n'
			macroSettings += '\\stylesheet{' + self._mapStyleFile + '}\n'
			formatSettings += '\\TitleColumns=1\n'
			formatSettings += '\\IntroColumns=1\n'
			formatSettings += '\\BodyColumns=1\n'
			# The next three will need some auto-tweaking depending on page size
			formatSettings += '\\def\TopMarginFactor{0.4}\n'
			formatSettings += '\\def\SideMarginFactor{1.5}\n'
			formatSettings += '\\def\BottomMarginFactor{1}\n'
			headerSettings += self.RemovePageNumbers(self._headerPositions)
			footerSettings += self.RemovePageNumbers(self._footerPositions)

			# In case the map has a rotation setting, just take the first part
			# of the map var
			for map in self._mapMatter :
				mapSettings += '\\ptxfile{' + self._pathToText + '/' + map.split()[0] + '.' + self._extWork + '}\n'

			mapSettings += '\\bye\n'

		else :
			# If we can't figure out what this is we have a system level bug and we might as well quite here
			self._log_manager.log("ERRR", "The context flag: " + self._contextFlag + " is not recognized by the system. Process halted.")
			return

		# The file header telling users not to touch it
		# This must go a little out of order because the
		# file name is being set above.
		fileHeaderText += '% File: ' + fileName + '\n\n' + \
			'% This file is auto generated. If you know what is good for you, will not edit it!\n\n'

		# General settings
		if justifyPars.lower() == 'false' :
			generalSettings = generalSettings + '\\JustifyParsfalse\n'

		if rightToLeft.lower() == 'true' :
			generalSettings = generalSettings + '\\RTLtrue\n'

		# Ship the results, change order as needed
		orderedContents =   fileHeaderText + \
							macroSettings + \
							formatSettings + \
							headerSettings + \
							footerSettings + \
							generalSettings + \
							mapSettings + \
							'\n'

		# We don't want to write out at this point if the file want to
		# write to already exists.
		if not os.path.isfile(fileName) :
			self.writeOutTheFile(orderedContents)
		else :
			self._log_manager.log("INFO", "Exists: " + os.path.split(self._outputFile)[1], "true")


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

		texControlObject = codecs.open(self._outputFile, "w", encoding='utf_8')
		texControlObject.write(contents)
		texControlObject.close()
		self._log_manager.log("DBUG", "Wrote out the file: " + self._outputFile)

	def parseThisBook (self, book) :
		'''Parse a specific book based on ID then return relevant info.'''

		# Get our current book object
		bookObject = "".join(codecs.open(book, "r", encoding='utf_8'))

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


