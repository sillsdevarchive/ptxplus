#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20080423
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This script handels the copying of text source files to the
# working directory. It is blind when it comes to encoding
# changes. Changing the encoding at copy time is seen more as
# a technique than a common practice. This is somewhat
# simplistic but should allow for more complex copy operations
# as it is developed further.

# History:
# 20080519 - djd - Initial draft
# 20080531 - djd - Changed to a class and moved to run through
#        the process_scripture_text.py script
# 20080627 - djd - Updated some of the initiation used tools
#        class to do this
# 20080731 - djd - Fixed a file name problem due to a system
#        file name change for periperal files.
# 20080821 - djd - Make changes to reflect the implementation
#        of flat file management (linear ouput processing)
# 20080826 - djd - Changed the copy command to be one that
#        comes from the project.conf file. This allows
#        us to customize it for encoding conversions.
# 20081020 - djd - Added a sanity check on the copy and fix
#        some bugs.
# 20081023 - djd - Refactored due to changes in project.conf
# 20081030 - djd - Added total dependence on log_manager.
#        This script will not run without it because
#        it handles all the parameters it needs.
# 20100622 - djd - Removed the reencodingRequired var which
#       changes the script to be encoding agnostic.


#############################################################
#################### Initialize The Process #################
#############################################################
# Firstly, import all the standard Python modules we need for
# this process

#import os, shutil, sys, re
import os, shutil, sys

# Import supporting local classes
import tools


class CopyFromSource (object) :


	def main(self, log_manager):

		log_manager._currentSubProcess = 'CpFrmSrc'

		# Pull out our parameters from the log_manager object
		settings = log_manager._settings
		inputFile = log_manager._currentInput
		outputFile =  log_manager._currentOutput

		# Pull in the command from the project.conf file
		copyCommand = settings['System']['Processes']['copyCommand']
		# Fix any case problems in the file placeholders (we want lc)
		copyCommand = copyCommand.replace('[inFile]', '[infile]')
		copyCommand = copyCommand.replace('[outFile]', '[outfile]')

		# Because we want to be able to customize the command if necessary the
		# incoming command has placeholders for the input and output. We need
		# to replace this here.
		tempFile = inputFile + '.tmp'
		copyCommand = copyCommand.replace('[infile]', inputFile)
		copyCommand = copyCommand.replace('[outfile]', tempFile)
		nfdCommand = 'txtconv -i ' + tempFile + ' -o ' + outputFile + ' -nfd '
		cleanCommand = 'rm ' + tempFile

		# Try the command and check to see if it was successful
		try :
			os.system(copyCommand)
			if os.path.isfile(tempFile) :
				log_manager.log("INFO", "Copied from: " + inputFile + " ---To:--> " + tempFile + " Command used: " + copyCommand)
			else :
				log_manager.log("ERRR", "File not found. The Copy command was executed but seemed to fail. Command executed: " + copyCommand)

		except :
			log_manager.log("ERRR", "Failed to execute: " + copyCommand)

		# Apply the NFD to insure the text it usable in the system
		# This relys on the TECKit txtconv utility to be present
		try :
			os.system(nfdCommand)
			if os.path.isfile(outputFile) :
				log_manager.log("INFO", "Normalized data to NFD in: " + outputFile)
			else :
				log_manager.log("ERRR", "File not found. The NFD normalization was executed but seemed to fail. Command executed: " + nfdCommand)

		except :
			log_manager.log("ERRR", "Failed to normalize to NFD: " + nfdCommand)

		# Remeber to wipe your feet
		try :
			os.system(cleanCommand)
			if not os.path.isfile(tempFile) :
				log_manager.log("INFO", "Removed temp file: " + tempFile)
			else :
				log_manager.log("ERRR", "Temp file was not removed: " + tempFile)

		except :
			log_manager.log("ERRR", "Failed to remove temp file: " + tempFile)


# This starts the whole process going
def doIt(log_manager):

	thisModule = CopyFromSource()
	return thisModule.main(log_manager)

