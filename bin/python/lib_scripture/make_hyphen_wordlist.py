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
		orgHyphenationFile = os.getcwd() + "/" + hyphenPath + "/hyphenation.txt"
		newHyphenationFile = os.getcwd() + "/" + hyphenPath + "/hyphenation.txt"
		prefixListFile = os.getcwd() + "/" + hyphenPath + "/prefixes.txt"
		suffixListFile = os.getcwd() + "/" + hyphenPath + "/suffixes.txt"
		hyphenList = {}
		wordlistReport = {}
		prefixList = []
		suffixList = []

		# We need to load files in order to avoid wasting time if something is not there
		# The assumption here is that all these files are in the same encoding and if
		# any changes are needed they will be applied to the final file we produce.
		# Note, the encoding should match the wordlist-master.txt file as it is made
		# by another process.

		# Is there a prefixList to process?
		if os.path.isfile(prefixListFile) :
			prefixListObject = codecs.open(prefixListFile, 'r', encoding='utf-8')
			# Push to a dictionary (w/o line endings)
			for line in prefixListObject :
				# BOM search and destroy
				line = re.compile(u'^\uFEFF').sub('',line)
				if line != "" :
					# Just in case they added the hyphen, strip it out
					line = line.replace('-', '')
					prefixList.append(line.strip())

			prefixListObject.close

		# How about suffixes, any of those?
		if os.path.isfile(suffixListFile) :
			suffixListObject = codecs.open(suffixListFile, 'r', encoding='utf-8')
			# Push to a dictionary (w/o line endings)
			for line in suffixListObject :
				# BOM search and destroy
				line = re.compile(u'^\uFEFF').sub('',line)
				if line != "" :
					# Just in case they added the hyphen, strip it out
					line = line.replace('-', '')
					suffixList.append(line.strip())

			prefixListObject.close

		# This is all about auto-generating hyphenated words. This can be
		# done a number of ways. If none of the above lists are found then
		# there is no sense going on. Do a reality check here.
		if len(prefixList) < 1 or len(suffixList) < 1 :
			self._log_manager.log("ERROR", "No prefix or suffix lists were found. Aborting process.")
			# Leave now
			return

		# Check for the wordlistReportFile, it is essential, abort if it is missing
		if os.path.isfile(wordlistReportFile) :
			wordlistReportObject = codecs.open(wordlistReportFile, "r", encoding='utf-8')
			# Push it into a dictionary w/o line endings
			for line in wordlistReportObject :
				# BOM search and destroy
				line = re.compile(u'^\uFEFF').sub('',line)
				if line != "" :
					wordlistReport[line.strip()] = 1

			wordlistReportObject.close()
		else :
			self._log_manager.log("ERROR", "The word list report file was not found. Aborting process.")
			# Leave now
			return

		# Check for existing hyphenation list file, if one is found we'll pull in the contents
		if os.path.isfile(orgHyphenationFile) :
			orgHyphenListObject = codecs.open(orgHyphenationFile, 'r', encoding='utf-8')
			# Push it into a dictionary w/o line endings
			for line in orgHyphenListObject :
				# BOM search and destroy
				line = re.compile(u'^\uFEFF').sub('',line)
				if line != "" :
					word = line.strip()
					hyphenList[word.replace('-', '')] = word

			orgHyphenListObject.close()
			# Rename the file with a .old extension
			os.rename(orgHyphenationFile, orgHyphenationFile.replace('.txt', '.old'))

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

		for word in wordlistReport :
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

		newHyphenationObject.close()


	def lencmp (self, a, b) :
		'''A little object comparison function for sorting.'''

		return cmp(len(b), len(a))


# This starts the whole process going
def doIt (log_manager) :

	thisModule = MakeHyphenWordlist()
	return thisModule.main(log_manager)
