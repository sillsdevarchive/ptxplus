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
		tmpHyphenationFile = os.getcwd() + "/" + hyphenPath + "/hyphenation.tmp"
		prefixListFile = os.getcwd() + "/" + hyphenPath + "/prefixes.txt"
		suffixListFile = os.getcwd() + "/" + hyphenPath + "/suffixes.txt"
		orgHyphenList = {}
		wordlistReport = {}
		prefixList = {}
		suffixList = {}
		hyphenCandidates = {}

		# We need to load files in order to avoid wasting time if something is not there
		# The assumption here is that all these files are in the same encoding and if
		# any changes are needed they will be applied to the final file we produce.
		# Is there a prefixList to process?
		if os.path.isfile(prefixListFile) :
			prefixListObject = codecs.open(prefixListFile, 'r', encoding='utf-8')
			# Push to a dictionary (w/o line endings)
			for line in prefixListObject :
				if line != "" :
					# Just in case they added the hyphen, strip it out
					line = line.replace('-', '')
					prefixList[line.strip()] = 1

			prefixListObject.close

		# How about suffixes, any of those?
		if os.path.isfile(suffixListFile) :
			suffixListObject = codecs.open(suffixListFile, 'r', encoding='utf-8')
			# Push to a dictionary (w/o line endings)
			for line in suffixListObject :
				if line != "" :
					# Just in case they added the hyphen, strip it out
					line = line.replace('-', '')
					suffixList[line.strip()] = 1

			prefixListObject.close

		# This is all about auto-generating hyphenated words. This can be
		# done a number of ways. If none of the above lists are found then
		# there is no sense going on. Do a reality check here.
		if len(prefixList) == 0 or len(suffixList) == 0 :
			os._exit()

		# Check for the wordlistReportFile, it is essential, abort if it is missing
		if os.path.isfile(wordlistReportFile) :
			wordlistReportObject = codecs.open(wordlistReportFile, "r", encoding='utf-8')
			# Push it into a dictionary w/o line endings
			for line in wordlistReportObject :
				if line != "" :
					wordlistReport[line.strip()] = 1

			wordlistReportObject.close()
		else :
			self._log_manager.log("ERROR", "The word list report file was not found. Aborting process.")
			os._exit()

		# Check for existing hyphenation list file, if one is found we'll pull in the contents
		os.path.isfile(orgHyphenationFile) :
			orgHyphenListObject = codecs.open(orgHyphenationFile, 'r', encoding='utf-8')
			# Push it into a dictionary w/o line endings
			for line in orgHyphenListObject :
				if line != "" :
					orgHyphenList[line.strip()] = 1

			orgHyphenListObject.close()
			# Rename the file with a .old extension
			os.rename(orgHyphenationFile, orgHyphenationFile.replace('.txt', '.old'))

		# If we made it this far the actual process can begin

		# Apply prefixes and suffixes to word list and create
		# new hyphenated words, add them to hyphenCandidates{}

		# build a regex for both prefixes and suffixes
		# Prefixes
		for p in prefixListObject :
			p = p.replace('-', '')
			pList = pList + p + '|'

		prefixes = "ur'^(" + pList.rstrip('|') + ")'"
		prefixTest = re.compile(prefixes)

		for word in wordlistReport :
			# What do we do with this?
			re.sub(prefixes, prefixes + '-', word, 1)



		# Suffixes
		suffixTest = re.compile(ur'(xxx|yyy|zzz)$')

		# Merge the hyphenCandidates with the orgHyphenList

		# Write out the new version of the hyphenation file

		# Apply any encoding conversions needed

		# Think more about file names and temp files needed...




# This starts the whole process going
def doIt (log_manager) :

	thisModule = MakeHyphenWordlist()
	return thisModule.main(log_manager)
