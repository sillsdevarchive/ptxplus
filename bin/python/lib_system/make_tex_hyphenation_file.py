#!/usr/bin/python
# -*- coding: utf-8 -*-
# version: 20080423
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This script will fresh TeX hyphenation instruction file for
# the current project.

# History:
# 20080526 - djd - Initial draft
# 20080609 - djd - Changed reference to master.ini file
# 20080623 - djd - Refined the names of the files so they
#		better reflect the language they are using.
# 20081028 - djd - Removed system logging, messages only now


#############################################################
######################### Load Modules ######################
#############################################################
# Firstly, import all the standard Python modules we need for
# this process

import sys, codecs, os

# Import supporting local classes
from tools import *
tools = Tools()


class MakeTexHyphenationFile (object) :


	def main (self, log_manager) :


		settings = tools.getSettingsObject()
		hyphenPath = settings['Process']['Paths']['PATH_HYPHENATION']
		lcCodeList = ""

		# Set the output file name and the wordlist file name
		texHyphenFileName = hyphenPath + "/hyphenation.tex"
		wordListFileName =  hyphenPath + "/hyphenation.txt"
		lcCodeListFileName = hyphenPath + "/lccodelist.txt"

		# Make the TeX hyphen file
		texHyphenFileObject = codecs.open(texHyphenFileName, "w", encoding='utf-8')

		# It may be necessary to have an lcCodeList included. These codes can be
		# kept in an external file or in a field in the project.conf called lcCode.
		# We will look for a file first, if we don't find one, we'll look in the
		# settings to see if there are any codes there. The file will override
		# anything in the settings. BTW, currently there are no dependencies on
		# this setting. It will work happily without it, but TeX may not. :-(
		if os.path.isfile(lcCodeListFileName) == True :
			lcCodeListObject = codecs.open(lcCodeListFileName, 'r', encoding='utf-8')
			for line in lcCodeListObject :
				lcCodeList = lcCodeList + line

			settings['TeX']['Hyphenation']['lcCode'] = lcCodeList

		# Check to see if the word list exsists. If it doesn't we will make a new one.
		# If it does exist we will not touch it so we don't lose any data.
		if os.path.isfile(wordListFileName) == False :
			# Just make the file, nothing else
			wordListFileObject = codecs.open(wordListFileName, 'w', encoding='utf-8')
			wordListFileObject.close()
		else :
			wordListFileObject = codecs.open(wordListFileName, 'r', encoding='utf-8')

			list = "\hyphenation{\n"
			for line in wordListFileObject :
				# This next line will handle the BOM if there is one in the file (at the begining)
				line = re.compile(u'^\uFEFF').sub('',line)
				# Take out any commented lines
				if line[:1] != "%" :
					list = list + line

			list = list + "}\n"
			settings["TeX"]["Hyphenation"]["hyphenWords"] = list

		# Make header line
		contents = 	"% hyphenation.tex\n" \
				"% This is an auto-generated hyphenation rules file for this project.\n" \
				"% Please refer to the documentation for details on how to make changes.\n\n"
		# Pickup our settings
		settingsToGet = settings['TeX']['Hyphenation']['FileSettings']
		for key, value in settingsToGet.iteritems() :
			contents = contents + value + "\n"


		# End here by writing out the contents we produced
		texHyphenFileObject.write(contents)

		# Tell the world what we did
		tools.userMessage("Wrote out file: " + texHyphenFileName)



# This starts the whole process going
def doIt(log_manager):

	thisModule = MakeTexHyphenationFile()
	return thisModule.main(log_manager)
