#!/usr/bin/python
# -*- coding: utf-8 -*-
# version: 20090120
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# Generate a list of hyphenated words based on supplied
# suffixes and prefixes and a word list. Then, if it is
# already there, merge it with the hyphenated word list
# in the hyphenation folder.

# History:
# 20090130 - djd - Initial draft


#############################################################
######################### Shell Class #######################
#############################################################

import codecs

# Import supporting local classes
from encoding_manager import *
from tools import *
tools = Tools()


class MakeHyphenWordlist (object) :

	def main (self, log_manager) :

# Change this to reflect the fact that we are working with a wordlist, not a Scripture file.
# actually don't work with any SFM here so we don't need the paser

		??? = log_manager._currentOutput

		# Get our word list object
		??? = "".join(codecs.open(log_manager._currentInput, "r", encoding='utf-8'))





# This starts the whole process going
def doIt (log_manager) :

	thisModule = MakeHyphenWordlist()
	return thisModule.main(log_manager)
