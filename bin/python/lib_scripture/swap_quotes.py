#!/usr/bin/python2
# -*- coding: utf_8 -*-
# version: 20081207
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This class will call on the check_quotes.py module
# and instruct it to swap one type of quotes for another.
# Example smart quotes for dumb or dumb for smart. Whatever
# the current system is, it will change it to the other.
# It uses the check_quotes.py module to do this by giving
# the mode command of "swap".

# History:
# 20080729 - djd - Initial draft
# 20081030 - djd - Added total dependence on log_manager.
#        This script will not run without it because
#        it handles all the parameters it needs.


#############################################################
######################### Shell Class #######################
#############################################################

import codecs
from parse_sfm import *
from encoding_manager import *
from check_quotes import *


class SwapQuotes (object) :


	def main (self, log_manager) :

		outputFile = log_manager._currentOutput

		# Get our book object - Using utf_8_sig because the source
		# might be coming from outside the system and we may need
		# to be able to handle a BOM.
		bookObject = "".join(codecs.open(log_manager._currentInput, "r", encoding='utf_8_sig'))

		# Load in the parser
		parser = parse_sfm.Parser()

		# This calls the quote checking module which should swap the quotes
		# because the output file should have been set. If it has, it will
		# output a file with quotes swapped
		parser.setHandler(QuoteContextHandler(log_manager, 'swap'))
		output = parser.transduce(bookObject)

		# The whole idea of this module is to swap quotes but we need to be
		# sure that an output file name exists.
		if outputFile != "none" or outputFile != "" :
			outputObject = codecs.open(outputFile, "w", encoding='utf_8')
			outputObject.write(output)


#############################################################################################################################

# This starts the whole process going
def doIt (log_manager):

	thisModule = SwapQuotes()
	return thisModule.main(log_manager)
