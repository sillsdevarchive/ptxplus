#!/usr/bin/python2.5
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
# 20090901 - te - Reorganized script and solidified the output
#		also took out some config settings that seem
#		redundant now


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

		# Set the output file name and the wordlist file name
		texHyphenFileName = hyphenPath + "/hyphenation.tex"
		wordListFileName =  hyphenPath + "/hyphenation.txt"
		lcCodeListFileName = hyphenPath + "/lccodelist.txt"

		# If we see that the texHyphenFile exists we will abort
		# That file needs to be manually removed to avoid problems
		if os.path.isfile(texHyphenFileName) == True :
			# Report that we found a .tex file and had to stop
			tools.userMessage("make_tex_hyphenation_file: The file, " + texHyphenFileName + " already exists. Process halted")
		else :
			# Just make the file, nothing else

################ Something is wrong with this next line ###################

			word_list_in = codecs.open(wordListFileName,
				mode='r' if os.path.isfile(wordListFileName) else 'rw',
				encoding='utf_8_sig')

###########################################################################

			# Make the TeX hyphen file
			tex_hypens_out = codecs.open(texHyphenFileName, "w", encoding='utf-8')
			# Make header line
			tex_hypens_out.write(
				"% hyphenation.tex\n"
				"% This is an auto-generated hyphenation rules file for this project.\n"
				"% Please refer to the documentation for details on how to make changes.\n\n")

			# Pickup our settings
			settingsToGet = settings['TeX']['Hyphenation']
			tex_hypens_out.writelines(v+'\n' for v in settingsToGet.values())

			# It may be necessary to have an lcCodeList included. These codes are
			# kept in an external file normally kept in the project hyphenation folder.
			if os.path.isfile(lcCodeListFileName):
				tex_hypens_out.writelines(codecs.open(lcCodeListFileName, 'r', encoding='utf_8_sig'))
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
			tools.userMessage("make_tex_hyphenation_file: Wrote out file: " + texHyphenFileName)



# This starts the whole process going
def doIt(log_manager):
#	import pdb
	thisModule = MakeTexHyphenationFile()
	return thisModule.main(log_manager)
#	return pdb.run(thisModule.main, log_manager)
