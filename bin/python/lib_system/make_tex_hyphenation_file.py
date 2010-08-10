#!/usr/bin/python2
# -*- coding: utf_8 -*-
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
#        better reflect the language they are using.
# 20081028 - djd - Removed system logging, messages only now
# 20090901 - te - Reorganized script and solidified the output
#        also took out some config settings that seem
#        redundant now
# 20100519 - djd - Fix some bad paths


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
		hyphenPath = settings['System']['Paths']['PATH_HYPHENATION']

		# Set the output file name and the wordlist file name
		texHyphenFileName   = hyphenPath + '/' + settings['System']['Files']['FILE_HYPHENATION_TEX']
		wordListFileName    =  hyphenPath + '/' + settings['System']['Files']['FILE_HYPHENATION_TXT']
		lcCodeListFileName  = hyphenPath + '/' + settings['System']['Files']['FILE_LCCODELIST_TXT']
		# Get our project hyphenation commands
		languageCode        = settings['ProjectText']['languageCode']
		setHyphenCharacter  = settings['Format']['Hyphenation']['setHyphenCharacter']
		setHyphenPenalty    = settings['Format']['Hyphenation']['setHyphenPenalty']
		setExHyphenPenalty  = settings['Format']['Hyphenation']['setExHyphenPenalty']
		setPretolerance     = settings['Format']['Hyphenation']['setPretolerance']

		# If we see that the texHyphenFile exists we will check to see if
		# the overwrite flag has been set.
		if os.path.isfile(texHyphenFileName) == True and log_manager._optionalPassedVariable != 'overwrite' :
				# Report that we found a .tex file and had to stop
				tools.userMessage("WARN: " + texHyphenFileName + " exists. Process halted")
		else :
			# Just make the file, nothing else

			# Open our wordlist file, if one exists, if not, make one
			if not os.path.isfile(wordListFileName) :
				word_list_in = codecs.open(wordListFileName, mode='w', encoding='utf_8')
			else :
				# Use utf_8_sig to open it in case it has a BOM in it!
				word_list_in = codecs.open(wordListFileName, mode='r', encoding='utf_8_sig')


			# Make the TeX hyphen file
			tex_hypens_out = codecs.open(texHyphenFileName, "w", encoding='utf_8')
			# Make header line
			tex_hypens_out.write(
				"% hyphenation.tex\n"
				"% This is an auto-generated hyphenation rules file for this project.\n"
				"% Please refer to the documentation for details on how to make changes.\n\n")

			# Insert the TeX hyphenation commands from our .project.conf file
			tex_hypens_out.write('\\newlanguage\\' + languageCode + 'language\n')
			tex_hypens_out.write('\\language = \\' + languageCode + 'language\n')
			tex_hypens_out.write('\\defaulthyphenchar=' + setHyphenCharacter + '\n')
			tex_hypens_out.write('\\hyphenpenalty=' + setHyphenPenalty + '\n')
			tex_hypens_out.write('\\exhyphenpenalty=' + setExHyphenPenalty + '\n')
			if setPretolerance != '' :
				tex_hypens_out.write('\\pretolerance=' + setPretolerance + '\n')

			# Spacer
			tex_hypens_out.write('\n\n')

			# It may be necessary to have an lcCodeList included. These codes are
			# kept in an external file normally kept in the project hyphenation folder.
			if os.path.isfile(lcCodeListFileName):
				tex_hypens_out.writelines(codecs.open(lcCodeListFileName, 'r', encoding='utf_8'))
				tex_hypens_out.write('\n')

			# The hyphenation word list is normally generated in another process
			# or it could be made by hand. It is normally kept in the project
			# hyphenation folder. This next block of code will copy across the
			# contents of the wordlist, skipping comments as we go.
			tex_hypens_out.write('\hyphenation{\n')
			tex_hypens_out.writelines(l for l in (l.lstrip() for l in word_list_in) if l[0] is not '%')
			tex_hypens_out.write('}\n')
			tex_hypens_out.close()

			# Tell the world what we did
			tools.userMessage("INFO: Created: " + texHyphenFileName)



# This starts the whole process going
def doIt(log_manager):

	thisModule = MakeTexHyphenationFile()
	return thisModule.main(log_manager)
