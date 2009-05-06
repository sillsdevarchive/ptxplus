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

import codecs, csv
from collections import defaultdict
from operator import itemgetter

# Import supporting local classes
from encoding_manager import *
from tools import *
tools = Tools()


class MakeHyphenWordlist (object) :

	def main (self, log_manager) :

		self._log_manager = log_manager
		reportPath = log_manager._settings['Process']['Paths']['PATH_REPORTS']
		hyphenPath = log_manager._settings['Process']['Paths']['PATH_HYPHENATION']
		wordlistReportFile = os.getcwd() + "/" + reportPath + "/wordlist-master.csv"
		sourceHyphenationFile = log_manager._settings['TeX']['Hyphenation']['sourceHyphenWords']
		newHyphenationFile = os.getcwd() + "/" + hyphenPath + "/hyphenation.txt"
		prefixListPath = log_manager._settings['TeX']['Hyphenation']['sourcePrefixes']
		suffixListFile = log_manager._settings['TeX']['Hyphenation']['sourceSuffixes']
		# Bring in any encoding mapings we may need.
		encodingChain = log_manager._settings['Encoding']['Processing']['encodingChain']
		hyphenList = {}
		wordlistReport = {}
		prefixList = []
		suffixList = []
		wordIntakeCount = 0
		prefixIntakeCount = 0
		suffixIntakeCount = 0
		hyphenWordCount = 0

		if encodingChain != "" :
			# Build the encoding engine(s)
			encodingChain = TxtconvChain([s.strip() for s in encodingChain.split(',')])

		# Load the exsiting hyphen words source list if one is in the source folder.
		# We will fill a dictionary here that was created above with the defaultdict
		# module. That will be used for the final output when we're done.
		if os.path.isfile(sourceHyphenationFile) :
			try :
				# We don't know exactly what the encoding of this file is. It is probably
				# Unicode, more than likely UTF-8. As such, we'll bring in the text raw,
				# then decode to Unicode. That should keep things working
				sourceHyphenListObject = open(sourceHyphenationFile, 'rb')

				# A problem can occur here where stray word-final punctuation or other
				# non-word-forming characters can get included in the word string.
				# It would be possible to remove them here but it would not be easy.
				# After much thought I have decided to rely on the translator to
				# provide clean data and any problems found will need to be edited
				# by hand to correct them.

				# Do an encoding conversion if necessary
				if encodingChain != "" :
					sourceHyphenListObject = encodingChain.convert(sourceHyphenListObject.read()).decode('utf-8').split('\n')

				# Push it into a dictionary w/o line endings
				for line in sourceHyphenListObject :
					if line != "" :
						word = line.strip()
						hyphenList[word.replace('-', '')] = word

				self._log_manager.log("INFO", sourceHyphenationFile + " loaded, found " + str(len(hyphenList)) + " words.")

			except UnicodeDecodeError, e :
				self._log_manager.log("ERRR", sourceHyphenationFile + ": " + str(e))
				return

		else :
				self._log_manager.log("DBUG", sourceHyphenationFile + " not found")

		# Now we will look for and load all the peripheral files and report
		# on what we found.

		# Check for the wordlistReportFile
		if os.path.isfile(wordlistReportFile) :
			try :
				wordlistReportObject = csv.reader(open(wordlistReportFile), dialect=csv.excel)
				for word,count in wordlistReportObject :
					wordlistReport[word.decode('utf-8')] = 1
					wordIntakeCount +=1

				self._log_manager.log("INFO", wordlistReportFile + " loaded, found " + str(wordIntakeCount) + " words.")

			# If there is a file to load and it fails we need to know about it
			except e :
				self._log_manager.log("ERRR", wordlistReportFile + ": " + str(e))
				return

			finally :
				pass
		else :
			self._log_manager.log("DBUG", wordlistReportFile + " was not found, continued process.")

		# Is there a prefixList to process?
		if os.path.isfile(prefixListPath) :
			try :
				prefixListFile = open(prefixListPath, 'rb')
				# Do an encoding conversion if necessary
				if encodingChain != "" :
					prefixListObject = encodingChain.convert(prefixListFile.read()).decode('utf-8').split('\n')

				# Push to a dictionary (w/o line endings)
				for line in prefixListObject :
					if line != "" :
						# Just in case they added of the many kinds of the hyphens, strip it out
						line = re.compile(u'^\u002D | \u2010 | \u2011 | \u2012 | \u2013 | \u2014').sub('',line, count = 0)
						#line = line.replace('-', '')
						prefixList.append(line.strip())
						prefixIntakeCount += 1

				self._log_manager.log("INFO", prefixListPath + " loaded, found " + str(prefixIntakeCount) + " words.")

			# If there is a file to load and it fails we need to know about it
			except UnicodeDecodeError, e :
				self._log_manager.log("ERRR", prefixListPath + ": " + str(e))
				return

			finally :
				prefixListFile.close()

		else :
				self._log_manager.log("DBUG", prefixListPath + " not found")

		# How about suffixes, any of those?
		if os.path.isfile(suffixListFile) :
			try :
				suffixListObject = open(suffixListFile, 'rb')
				# Do an encoding conversion if necessary
				if encodingChain != "" :
					suffixListObject = encodingChain.convert(suffixListObject.read()).decode('utf-8').split('\n')
				# Push to a dictionary (w/o line endings)
				for line in suffixListObject :
					if line != "" :
						# Just in case they added of the many kinds of the hyphens, strip it out
						line = re.compile(u'^\u002D | \u2010 | \u2011 | \u2012 | \u2013 | \u2014').sub('',line, count = 0)
						#line = line.replace('-', '')
						suffixList.append(line.strip())
						suffixIntakeCount += 1

				self._log_manager.log("INFO", suffixListFile + " loaded, found " + str(suffixIntakeCount) + " words.")

			# If there is a file to load and it fails we need to know about it
			except UnicodeDecodeError, e :
				self._log_manager.log("ERRR", suffixListFile + ": " + str(e))
				return

		else :
				self._log_manager.log("DBUG", suffixListFile + " not found")

		# This part is all about auto-generating hyphenated words. This can
		# be done a number of ways. Test to see if we have enough of the
		# above objects to auto-generate some hyphenated words. If not
		# we will just move on to see if there is an existing list we can use.
		if wordIntakeCount > 0:
			if prefixList or suffixList:
				# If we made it this far the actual process can begin

				# Apply prefixes and suffixes to word list and create
				# new hyphenated words, add them to hyphenCandidates{}

				# Build a regex for both prefixes and suffixes
				pList = ""
				sList = ""
				prefixList.sort(self.lencmp)
				suffixList.sort(self.lencmp)
				# Populate the lists
				for p in prefixList :
					p = p.replace('-', '')
					pList = pList + p + '|'

				for s in suffixList :
					s = s.replace('-', '')
					sList = sList + s + '|'
				# Make the Regex
				prefixes = "^(?ui)(" + pList.rstrip('|') + ")(?=\w)"
				prefixTest = re.compile(prefixes)
				suffixes = "(?ui)(?<=\w)(" + sList.rstrip('|') + ")$"
				suffixTest = re.compile(suffixes)

# Problem: For some reason we have a very large difference between two scripts tested in
# the same langague. We'd expect similar results but it is off by thousands. I think it is
# happening around here in the code. At this point there are some encoding issues to fix
# so until that is done there is no point testing any further. This remains an open issue.

				for word in wordlistReport :
					if word != "" :
						m = prefixTest.sub(r"\1-", word)
						m = suffixTest.sub(r"-\1", m)
						if m.find('-') > -1 and not hyphenList.has_key(word) and m.rfind('-') < len(m) - 1 :
							hyphenList[word] = m

#######################################################################################

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

		self._log_manager.log("DBUG", "Hyphenated word list created, made " + str(hyphenWordCount) + " words.")
		newHyphenationObject.close()


	def lencmp (self, a, b) :
		'''A little object comparison function for sorting.'''

		return cmp(len(b), len(a))


# This starts the whole process going
def doIt (log_manager) :

	thisModule = MakeHyphenWordlist()
	return thisModule.main(log_manager)
