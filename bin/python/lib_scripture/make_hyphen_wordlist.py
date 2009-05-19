#!/usr/bin/python2.5
# -*- coding: utf-8 -*-
# version: 20090120
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# Generate a list of hyphenated words based on supplied
# suffixes and prefixes and a word list that are part of
# the source text. This script will look for these files
# in the specified location and process them. The results
# are a hyphenated word list in the Hyphenation folder which
# can be used by another process to create the actual file
# TeX will use for hyphenation on the text.

# History:
# 20090130 - djd - Initial draft
# 20090327 - djd - Draft is working but issues remain over
#		output discrepancies. This needs to be revisited
#		later after some other larger issues are settled.


#############################################################
######################### Shell Class #######################
#############################################################

import codecs, csv, sys
from collections import defaultdict
from operator import itemgetter

# Import supporting local classes
from encoding_manager import *
from tools import *
tools = Tools()


class MakeHyphenWordlist (object) :

	def main (self, log_manager) :
		self._log_manager = log_manager
		self._hyphens_re = re.compile(u'\u002D|\u2010|\u2011|\u2012|\u2013|\u2014|\ufeff')
		reportPath = log_manager._settings['Process']['Paths']['PATH_REPORTS']
		hyphenPath = log_manager._settings['Process']['Paths']['PATH_HYPHENATION']
		wordlistReportFile = os.getcwd() + "/" + reportPath + "/wordlist-master.csv"
		sourceHyphenationFile = log_manager._settings['TeX']['Hyphenation']['sourceHyphenWords']
		newHyphenationFile = os.getcwd() + "/" + hyphenPath + "/hyphenation.txt"
		prefixListPath = log_manager._settings['TeX']['Hyphenation']['sourcePrefixes']
		suffixListFile = log_manager._settings['TeX']['Hyphenation']['sourceSuffixes']
		# Bring in any encoding mapings we may need.
		self._encodingChain = log_manager._settings['Encoding']['Processing']['encodingChain']
		wordlistReport = set()
		prefixList = []
		suffixList = []
		wordIntakeCount = 0
		prefixIntakeCount = 0
		suffixIntakeCount = 0
		hyphenWordCount = 0

		if self._encodingChain:
			# Build the encoding engine(s)
			self._encodingChain = TxtconvChain([s.strip() for s in self._encodingChain.split(',')])

		# Load the exsiting hyphen words source list if one is in the source folder.
		# We will fill a dictionary here that was created above with the defaultdict
		# module. That will be used for the final output when we're done.

		# A problem can occur here where stray word-final punctuation or other
		# non-word-forming characters can get included in the word string.
		# It would be possible to remove them here but it would not be easy.
		# After much thought I have decided to rely on the translator to
		# provide clean data and any problems found will need to be edited
		# by hand to correct them.
		words = self.wordListFromFile(sourceHyphenationFile)
		hyphenList = dict(zip(self.cleanWordList(words),words))

		# Now we will look for and load all the peripheral files and report
		# on what we found.

		# Check for the wordlistReportFile
		if os.path.isfile(wordlistReportFile) :
			try :
				wordlistReportObject = csv.reader(open(wordlistReportFile), dialect=csv.excel)
				for w in (w.decode('utf-8').translate({0xfeff:None}) for w,c in wordlistReportObject):
					if not self._hyphens_re.search(w):
						wordlistReport.add(w)
					else:
						self._log_manager.log("INFO", "Input word already hyphenated: " + w)
				self._log_manager.log("INFO", wordlistReportFile + " loaded, found " + str(len(wordlistReport)) + " words.")
			# If there is a file to load and it fails we need to know about it
			except :
				self._log_manager.log("ERRR", wordlistReportFile + ": " + str(sys.exc_info()))
				return
		else :
			self._log_manager.log("DBUG", wordlistReportFile + " was not found, continued process.")

		# Is there a prefixList to process?
		suffixList = self.cleanWordList(self.wordListFromFile(prefixListPath))
		# How about suffixes, any of those?
		prefixList = self.cleanWordList(self.wordListFromFile(suffixListFile))

		# This part is all about auto-generating hyphenated words. This can
		# be done a number of ways. Test to see if we have enough of the
		# above objects to auto-generate some hyphenated words. If not
		# we will just move on to see if there is an existing list we can use.
		if wordlistReport:
			if prefixList or suffixList:
				# If we made it this far the actual process can begin

				# Apply prefixes and suffixes to word list and create
				# new hyphenated words, add them to hyphenCandidates{}

				# Build a regex for both prefixes and suffixes
				prefixList.sort(key=len)
				suffixList.sort(key=len)
				pList = '|'.join(prefixList)
				sList = '|'.join(suffixList)

				# Make the Regex
				prefixes = "^(?ui)(" + pList + ")(?=.)"
				prefixTest = re.compile(prefixes)
				suffixes = "(?ui)(?<=[^\-])(" + sList + ")$"
				suffixTest = re.compile(suffixes)

				for word in wordlistReport :
					m = prefixTest.sub(r"\1-", word)
					m = suffixTest.sub(r"-\1", m)
					if '-' in m and not hyphenList.has_key(word) and m[-1] != '-' :
						hyphenList[word] = m
			else:
				self._log_manager.log("DBUG", "Could not generate any hyphenated words, no prefix or suffix files found.")
		else :
			self._log_manager.log("ERRR", "Could not generate any hyphenated, Word list not found.")

		# Output the masterWordlist to the masterReportFile (simple word list)
		newHyphenationObject = codecs.open(newHyphenationFile, "w", encoding='utf-8')
		# Turn the hyphenList to a list and sort it
		hyphenkeys = hyphenList.items()
		hyphenkeys.sort(key=itemgetter(0))
		# Output the words
		for k,v in hyphenkeys :
			newHyphenationObject.write(v + "\n")
			hyphenWordCount += 1

#			self._log_manager.log("DBUG", "Hyphenated word list created, made " + str(hyphenWordCount) + " words.")
		newHyphenationObject.close()

	def cleanWordList(self, words):
		return [self._hyphens_re.sub('',w) for w in words]

	def wordListFromFile(self, file_path):
		word_list = []
		if os.path.isfile(file_path) :
			try :
				# We don't know exactly what the encoding of this file is. It is probably
				# Unicode, more than likely UTF-8. As such, we'll bring in the text raw,
				# then decode to Unicode. That should keep things working
				f = open(file_path, 'rb')

				# Do an encoding conversion if necessary
				if self._encodingChain:
					sourceHyphenListObject = self._encodingChain.convert(f.read()).decode('utf-8').split('\n')

				# Push it into a dictionary w/o line endings
				word_list = [l for l in (line.strip() for line in sourceHyphenListObject) if l]

				self._log_manager.log("INFO", file_path + " loaded, found " + str(len(word_list)) + " words.")

			except UnicodeDecodeError, e :
				self._log_manager.log("ERRR", file_path + ": " + str(e))
				return []
			finally :
				f.close()
		else :
				self._log_manager.log("DBUG", file_path + " not found")
		return word_list



# This starts the whole process going
def doIt (log_manager) :

	thisModule = MakeHyphenWordlist()
	return thisModule.main(log_manager)
