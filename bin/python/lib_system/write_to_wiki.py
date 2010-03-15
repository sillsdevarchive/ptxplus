#!/usr/bin/python
# -*- coding: utf-8 -*-
# version: 20081025
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This script will facilitate writing to project wiki files.
# This is for auto message insertion and date stamping. This
# currently does not support logging.

# History:
# 20081025 - djd - Initial draft. Implemented basic functions.


#############################################################
######################### Load Modules ######################
#############################################################
# Firstly, import all the modules we need for this process

import os, sys
from datetime import *

# Import supporting local classes
from tools import *
tools = Tools()

# These are the arguments passed by makefile
insertType = sys.argv[1]
wikiFile = sys.argv[2]


class WriteToWiki (object) :


	def main (self, insertType, wikiFile) :
		'''This manages the process of writing to project wikis'''

		# Get the user name
		userName = tools.getSystemUser()

		# Add a time stamp for notes and issues. More functions
		# will be added as I think of them. :-)
		if insertType == "issue" :
			stamp = "**" + str(datetime.now()).split('.')[0] + "**\nLogged By: **" + userName + "**\nStatus: **Open**\n<Enter Issue Here>\n\n"
			if tools.prependText(stamp, wikiFile) != True :
				# This doesn't support log file output so for
				# now we'll just write a simple error to the
				# terminal if it fails.
				tools.userMessage('Error: write_to_wiki.py has failed to output to the target wiki file which is: [' + wikiFile + '] The insertType used was: [' + insertType + ']')

		elif insertType == "note" :
			stamp = "**" + str(datetime.now()).split('.')[0] + "**\nLogged By: **" + userName + "**\n<Enter Note Text>\n\n"
			if tools.prependText(stamp, wikiFile) != True :
				# This doesn't support log file output so for
				# now we'll just write a simple error to the
				# terminal if it fails.
				tools.userMessage('Error: write_to_wiki.py has failed to output to the target wiki file which is: [' + wikiFile + '] The insertType used was: [' + insertType + ']')

		elif insertType == "about" :
			print "Writing about file."
			settings = tools.getSystemSettings()
			aboutText = settings['System']['aboutText']
			object = codecs.open(wikiFile, "w", encoding='utf_8_sig')
			object.write('=About: ptxplus=\n')
			object.write('Version ' + '\n\n')
			object.write(aboutText)
			object.close()

		else:
			tools.userMessage('Error: write_to_wiki.py did not complete the process. It does not support the [' + insertType + '] insert type. This is an incorrect value passed by makefile.')


# Run the process called on
runClass = WriteToWiki()
runClass.main(insertType, wikiFile)
