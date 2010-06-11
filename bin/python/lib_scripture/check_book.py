#!/usr/bin/python
# -*- coding: utf-8 -*-
# version: 20080729
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This module will perform various checks on the current book
# file as found in the log_manager object. The process starts
# by parsing the book with the SFM parser which then hands off
# chunks of text to checking classes.

# History:
# 20081128 - djd - Initial draft
# 20090505 - djd - Added a filter for peripheral matter files


#############################################################
######################### Shell Class #######################
#############################################################

import codecs
from parse_sfm import *
from check_sfm import *
from check_punctuation import *
from check_quotes import *
# Import supporting local classes
from tools import *
tools = Tools()


class CheckBook (object) :

	def main (self, log_manager) :

		# Filter out any peripheral files now
		# Note that the isPeripheralMatter() function is now
		# disabled. Do we really need to do this check anyway?
		# Let's go away and think about it
#        if tools.isPeripheralMatter(log_manager._currentInput) :
#
#            return


		# Get our book object
		bookObject = "".join(codecs.open(log_manager._currentInput, "r", encoding='utf_8_sig'))

		# Load in the parser
		parser = parse_sfm.Parser()

		# SFM Checking
		parser.setHandler(SFMContextHandler(log_manager))
		log_manager._currentSubProcess = 'ChkSFM'
		parser.parse(bookObject)

		# Punctuation Checking
		parser.setHandler(PunctuationContextHandler(log_manager))
		log_manager._currentSubProcess = 'ChkPnc'
		parser.parse(bookObject)

		# Quote Checking
		parser.setHandler(QuoteContextHandler(log_manager, 'check'))
		log_manager._currentSubProcess = 'ChkQts'
		# Last arg. is strict meaning yell when USFM rules are broken
		parser.parse(bookObject)

		# Other checks that could be supported would be:
		#    Footnotes
		#    Cross References


# This starts the whole process going
def doIt (log_manager):

	thisModule = CheckBook()
	return thisModule.main(log_manager)

