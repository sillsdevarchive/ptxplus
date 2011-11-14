#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20080702
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This class will create a dynamic .sty file for a TeX
# ptx2pdf typesetting project. It will create a .sty file
# based on the project's source files with adjustments made
# from variables found in the project.conf file.

# History:
# 20090114 - djd - Initial draft


#############################################################
#################### Initialize The Process #################
#############################################################
# Firstly, import all the standard Python modules we need for
# this process
import codecs
import parse_sfm
#import parse_sty

# Import supporting local classes
import tools


class MakeStyleFile (object) :

# Problem here! run_system_process.py doesn't use the log_manager so it doesn't pass it on to this module

	def main (self, log_manager) :

		inventoryObject = []
		# This is the style file we will write to
		styleFile = log_manager._settings['Process']['Files']['FILE_TEX_STYLE']

		# Load in the parser
		#sfmParser = parse_sfm.Parser()

		# Set the handler
		#sfmParser.setHandler(SFMInventoryHandler(log_manager))

		# Get an inventory of all the sfms used in this project
		# by parsing every book in the project. _currentInput
		# should contain a list of all the files. We will loop
		# through those and collect all our tags.

		processPath = log_manager._settings['Process']['Paths']['PATH_PROCESS']
		otBookList = log_manager._settings['Process']['Binding']['MATTER_OT']
		ntBookList = log_manager._settings['Process']['Binding']['MATTER_NT']

		for bn in (otBookList, ntBookList) :
			bookList = bookList + os.getcwd() + "/" + processPath + "/" + bn + ".usfm, "
			print bookList

		#for book in bookList :

			# Get our book object - Using utf_8_sig because the source
			# might be coming from outside the system and we may need
			# to be able to handle a BOM.
			#bookObject = "".join(codecs.open(book, "r", encoding='utf_8_sig'))
			# The parser needs to acumulate the sfms as it goes
			# through each book
			#inventoryObject = sfmParser.parse(bookObject)


		# Load in the style parser
		#styParser = parse_sty.Parser()
		#styleObject = styParser.parse(styleFile)

		# Here we need to merge the two objects to make
		# a new style file


		# Output the new style file
		#newStyleObject = codecs.open(newStyleFile, "w", encoding='utf_8_sig')
		#newStyleFile.write(newStyleObject)


class SFMInventoryHandler (parse_sfm.Handler) :
	'''This class replaces the Handler class in the parse_sfm module. As we are
		just preforming a simple task here this is a very stripped down version.'''


	def start (self, tag, num, info, prefix) :
		'''This tells us when a tag starts. We will use this information to set location
			and trigger events.'''

		# All we want to do here is generate a list of tags so we'll
		# just pass this one back

		return tag

	def text (self, text, tag, info) :
		'''This function allows us to harvest the text from a given text element. This will
			be used to check for quotes.'''

		# Nothing to do here
		return


	def end (self, tag, ctag, info) :
		'''This function tells us when an element is closed. We will
			use this to mark the end of events.'''

		# or here
		return


	def error (self, tag, text, msg) :
		'''Send any errors the parser finds back to the calling application.'''

		# or here
		pass


# This starts the whole process going
def doIt (log_manager) :

	thisModule = MakeStyleFile()
	return thisModule.main(log_manager)
