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

		self._log_manager = log_manager
		reportPath = log_manager._settings['Process']['Paths']['PATH_REPORTS']
		hyphenPath = log_manager._settings['Process']['Paths']['PATH_HYPHENATION']
		wordlistReportFile = os.getcwd() + "/" + reportPath + "/wordlist-master.txt"
		hyphenationFile = os.getcwd() + "/" + hyphenPath + "/hyphenation.txt"
		prefixListFile = os.getcwd() + "/" + hyphenPath + "/prefixes.txt"
		suffixListFile = os.getcwd() + "/" + hyphenPath + "/suffixes.txt"

		# Check for the wordlistReportFile, it is essential, abort if it is missing
		if os.path.isfile(wordlistReportFile) :
			masterWordlistObject = codecs.open(wordlistReportFile, "r", encoding='utf-8')
			# Push it into a dictionary w/o line endings
			for line in masterWordlistObject :
				if line != "" :
					masterWordlist[line.strip()] = 1

			masterWordlistObject.close()
		else :
			self._log_manager.log("ERROR", "The word list report file was not found. Aborting process.")
			os._exit()



		??? = log_manager._currentOutput

		# Get our word list object
		??? = "".join(codecs.open(log_manager._currentInput, "r", encoding='utf-8'))





# This starts the whole process going
def doIt (log_manager) :

	thisModule = MakeHyphenWordlist()
	return thisModule.main(log_manager)
