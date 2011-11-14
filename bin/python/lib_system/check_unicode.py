#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20100707
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This script will check a file for encoding problems. It will
# throw an error if any are found.

# History:
# 20100816 - djd - Initial draft


#############################################################
######################### Load Modules ######################
#############################################################
# Firstly, import all the modules we need for this process

import sys, os, codecs, unicodedata

class CheckUnicode (object) :


	def main (self, log_manager) :
		'''This is very simple module for checking the input
			file from the current set of processes that will
			be passed on to this module via the log_manager.'''

		log_manager._currentSubProcess = 'CkUnicode'
		log_manager._currentLocation = ""
		log_manager._currentContext = ""
		unicodeNormalForm = log_manager._settings['ProjectText']['WorkingText']['Encoding'].get('normalForm')

		# Much more could be done with this but for now we are just
		# going to look for U+FFFD which indicates some kind of typo,
		# or a null character in the file.
		if log_manager._currentInput != '' :
			inputFile = log_manager._currentInput

			if os.path.isfile(inputFile) == True :
				try:
					path, fName = os.path.split(inputFile)
					for num, line in enumerate(codecs.open(inputFile, "r", encoding='utf_8_sig'),start=1) :
						# Check for bad characters
						if u'\ufffd' in line or u'\u0000' in line :
							for word in line.split() :
								if u'\ufffd' in word or u'\u0000' in word :
									log_manager._currentLocation = fName + " - Line: " + str(num)
									log_manager._currentContext = word
									log_manager.log("ERRR", "Unicode issue detected")
						# Check for NFD or NFC if set
						if unicodeNormalForm != '' :
							normLine = unicodedata.normalize(unicodeNormalForm, line)
							if normLine != line :
								for word in line.split() :
									normWord = unicodedata.normalize(unicodeNormalForm, word)
									if normWord != word :
										log_manager._currentLocation = fName + " - Line: " + str(num)
										log_manager._currentContext = word
										log_manager.log("ERRR", "Failed Normalization test (" + unicodeNormalForm + ") should be: " + normWord)

				except :
					log_manager.log("ERRR", "Could not open " + log_manager._currentInput + " to do a Unicode sanity check")


# This starts the whole process going
def doIt(log_manager):

	thisModule = CheckUnicode()
	return thisModule.main(log_manager)

