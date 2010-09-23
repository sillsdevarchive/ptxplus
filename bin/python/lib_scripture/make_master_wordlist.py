#!/usr/bin/python2
# -*- coding: utf_8 -*-
# version: 20090120
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# Generate a word list for the current book being processed.
# This will parse the book and generate a word list and put
# it in the Reports folder.

# History:
# 20090130 - djd - Initial draft


#############################################################
######################### Shell Class #######################
#############################################################

import codecs, os, csv

# Import supporting local classes
from encoding_manager import *
import tools
from threading import Thread
from collections import defaultdict
from operator import itemgetter


class MakeWordlist (object) :

	def main (self, log_manager) :

		self._log_manager = log_manager
		log_manager._currentSubProcess = 'MasterWordlist'
		wordlistPath = tools.pubInfoObject['Paths']['PATH_WORDLISTS']
		masterReportFile = log_manager._currentOutput
		masterWordlistFlag = False
		masterWordlist = {}
		bookWordlist = {}
		uniqueWords = 0
		totalWords = 0

		# Use the defaultdict module to create the master word dictionary
		# Info on this module can be found here:
		# http://docs.python.org/library/collections.html?highlight=defaultdict#collections.defaultdict
		masterWordlist = defaultdict(int)

		fileList = os.listdir(wordlistPath)
		for fileName in fileList :
			if fileName.find('-wordlist.csv') > 0 :
				rptObject = csv.reader(open(wordlistPath + "/" + fileName), dialect=csv.excel)
				for word,count in rptObject :
					masterWordlist[word] += int(count)


		# Now that we have a complete master wordlist object we can
		# output to the master word list.
		cvsMasterFile = csv.writer(open(masterReportFile, "w"), dialect=csv.excel)
		# Convert the dictionary to a list
		rows = masterWordlist.items()
		# Get some count info
		uniqueWords = len(rows)
		totalWords = sum(masterWordlist.values())
		# Sort the list by case insensitive default unicode sort order.
		# this makes it easier to compare wordlists by diff
		rows.sort()
		rows.sort(key=lambda (w,c): w.lower())
		# Now write out the wordlist to the cvs file
		cvsMasterFile.writerows(rows)

		# Report what happened
		self._log_manager.log("INFO", "Process complete. Total words = " + str(totalWords) + " / Unique words = " + str(uniqueWords))
		self._log_manager.log("INFO", "Output sent to: " + masterReportFile)


# This starts the whole process going
def doIt (log_manager) :

	thisModule = MakeWordlist()
	return thisModule.main(log_manager)

