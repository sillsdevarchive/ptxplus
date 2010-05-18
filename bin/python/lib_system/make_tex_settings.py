#!/usr/bin/python
# -*- coding: utf-8 -*-
# version: 20100516
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This script will auto-generate the TeX macro setup file.
# It will define the document to the ptx2pdf macro system and
# will include things like page size, columns, etc. A custom
# settings file will be linked to this one that will contain
# special tweaks for individual projects.

# History:
# 20100516 - djd - Initial draft


#############################################################
######################### Load Modules ######################
#############################################################
# Firstly, import all the modules we need for this process

import sys, os, codecs

# Import supporting local classes
from tools import *
tools = Tools()


class MakeTexSettings (object) :


	def main (self, log_manager) :
		'''This is the main process function for generating the TeX setup file.
			Some of the settings will be found in the control file as they need
			to be associated with the object that is being processed.'''

		log_manager = log_manager
		log_manager._currentSubProcess = 'MkTexSettings'

		# Pull in global settings
# Use the .get() extention on all these settings so a default can be set

		# Build some paths and file names
		texMacros = log_manager._settings['Process']['Files']['FILE_TEX_MACRO']
		setupFile = os.getcwd() + "/" + log_manager._settings['Process']['Files']['FILE_TEX_SETUP']
		styleFile = os.getcwd() + "/" + log_manager._settings['Process']['Files']['FILE_TEX_STYLE']
		customSetup = os.getcwd() + "/" + log_manager._settings['Process']['Files']['FILE_TEX_SETUP_CUSTOM']
		tocTitle = log_manager._settings['Process']['TOC']['mainTitle']

		# Create the file header
		header = "% tex_settings.txt\n\n% This is an auto-generated file, do not edit. Any necessary changes\n" + \
				"% should be made to the project.conf file or the custom TeX setup file.\n\n"


		# Output to the new makefile file
		# Create the new TeX settings object (overwrite the old file)
		settingsFileObject = codecs.open(setupFile, 'w', encoding='utf_8_sig')
		settingsFileObject.write(header)
		settingsFileObject.write('\\input ' + texMacros + '\n')
		# Now put out the custom macro file path (this may need to be moved)
		settingsFileObject.write('\\input ' + customSetup + '\n')
		# Add the global style sheet
		settingsFileObject.write('\\stylesheet{' + styleFile + '}\n')
		settingsFileObject.close()


# This starts the whole process going
def doIt(log_manager):
	thisModule = MakeTexSettings()
	return thisModule.main(log_manager)
