#!/usr/bin/python2
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

import sys, os, codecs

class CheckUnicode (object) :


	def main (self, log_manager) :
		'''This is very simple module for checking the input
			file from the current set of processes that will
			be passed on to this module via the log_manager.'''

		log_manager._currentSubProcess = 'CkUnicode'
		log_manager._currentLocation = ""
		log_manager._currentContext = ""

		# Much more could be done with this but for now we are just
		# going to look for U+FFFD which indicates some kind of typo,
		# or a null character in the file.
		if log_manager._currentInput != '' :
			inputFile = log_manager._currentInput

			if os.path.isfile(inputFile) == True :
				try:
					head, tail = os.path.split(inputFile)
					for n, l in enumerate(codecs.open(inputFile, "r", encoding='utf_8_sig'),start=1) :
						if u'\ufffd' in l or u'\u0000' in l :
							log_manager._currentLocation = "Line: " + str(n)
							log_manager._currentContext = tail
							log_manager.log("ERRR", "Unicode issue detected")
				except :
					log_manager.log("ERRR", "Could not open " + log_manager._currentInput + " to do a Unicode sanity check")


# This starts the whole process going
def doIt(log_manager):

	thisModule = CheckUnicode()
	return thisModule.main(log_manager)
