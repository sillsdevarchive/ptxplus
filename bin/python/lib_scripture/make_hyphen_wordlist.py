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
# suffixes and prefixes and a word list that are part of
# the source text. This script will look for these files
# in the specified location and process them. The results
# are a hyphenated word list in the Hyphenation folder which
# can be used by another process to create the actual file
# TeX will use for hyphenation on the text.

# History:
# 20090130 - djd - Initial draft


#############################################################
######################### Shell Class #######################
#############################################################

import codecs, csv
from collections import defaultdict

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
		prefixListFile = log_manager._settings['TeX']['Hyphenation']['sourcePrefixes']
		suffixListFile = log_manager._settings['TeX']['Hyphenation']['sourceSuffixes']
		# Bring in any encoding mapings we may need.
		encodingChain = log_manager._settings['Encoding']['Processing']['encodingChain']
		hyphenList = defaultdict(int)
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

			#finally:
				#sourceHyphenListObject.close

		else :
				self._log_manager.log("DBUG", sourceHyphenationFile + " not found")

		# Now we will look for and load all the peripheral files and report
		# on what we found.

		# Check for the wordlistReportFile
		if os.path.isfile(wordlistReportFile) :
			try :
				wordlistReportObject = csv.reader(open(wordlistReportFile), dialect=csv.excel)
				for word,count in wordlistReportObject :
					wordlistReport[word] = 1
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
		if os.path.isfile(prefixListFile) :
			try :
				prefixListObject = open(prefixListFile, 'rb')
				# Do an encoding conversion if necessary
				if encodingChain != "" :
					prefixListObject = encodingChain.convert(prefixListObject.read()).decode('utf-8').split('\n')

				# Push to a dictionary (w/o line endings)
				for line in prefixListObject :
					if line != "" :
						# Just in case they added of the many kinds of the hyphens, strip it out
						line = re.compile(u'^\u002D | \u2010 | \u2011 | \u2012 | \u2013 | \u2014').sub('',line, count = 0)
						#line = line.replace('-', '')
						prefixList.append(line.strip())
						prefixIntakeCount += 1

				self._log_manager.log("INFO", prefixListFile + " loaded, found " + str(prefixIntakeCount) + " words.")

			# If there is a file to load and it fails we need to know about it
			except UnicodeDecodeError, e :
				self._log_manager.log("ERRR", prefixListFile + ": " + str(e))
				return

			#finally:
				#prefixListObject.close

		else :
				self._log_manager.log("DBUG", prefixListFile + " not found")


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

			#finally:
				#suffixListObject.close

		else :
				self._log_manager.log("DBUG", suffixListFile + " not found")

		# This part is all about auto-generating hyphenated words. This can
		# be done a number of ways. Test to see if we have enough of the
		# above objects to auto-generate some hyphenated words. If not
		# we will just move on to see if there is an existing list we can use.
		if wordIntakeCount > 0 and  len(prefixList) < 0 or len(suffixList) < 0 :
			self._log_manager.log("ERRR", "Could not generate any hyphenated words with the resources loaded.")
		else :
			# If we made it this far the actual process can begin

			# Apply prefixes and suffixes to word list and create
			# new hyphenated words, add them to hyphenCandidates{}

			# Build a regex for both prefixes and suffixes
			pList = ""
			sList = ""
			# Prefixes
			prefixList.sort(self.lencmp)
			suffixList.sort(self.lencmp)
			for p in prefixList :
				p = p.replace('-', '')
				pList = pList + p + '|'

			for s in suffixList :
				s = s.replace('-', '')
				sList = sList + s + '|'

			prefixes = "^(?ui)(" + pList.rstrip('|') + ")(?=\w)"
			prefixTest = re.compile(prefixes)
			suffixes = "(?ui)(?<=\w)(" + sList.rstrip('|') + ")$"
			suffixTest = re.compile(suffixes)

# Problem here!!!!!!!!!!!!!!!!!!!!

			for word in wordlistReport :
				print word
				if word != "" :
					m = prefixTest.sub(r"\1-", word)
					m = suffixTest.sub(r"-\1", m)
					if m.find('-') > -1 and not hyphenList.has_key(word) and m.rfind('-') < len(m) - 1 :
						hyphenList[word] = m

		# Output the masterWordlist to the masterReportFile (simple word list)
		newHyphenationObject = codecs.open(newHyphenationFile, "w", encoding='utf-8')

		debugObject = codecs.open("test.txt", "w", encoding='utf-8')

		hyphenkeys = hyphenList.keys()
		hyphenkeys.sort()
		for k in hyphenkeys :
			debugObject.write(k + " " + hyphenList[k] + "\n")
			newHyphenationObject.write(hyphenList[k] + "\n")
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
