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
		'''This is the main process function for generating the makefile.'''

		self._log_manager = log_manager

		# Create the new TeX settings object (overwrite the old file)
		settingsFileObject = codecs.open('tex_settings.txt', 'w', encoding='utf_8_sig')

		# Create the file header
		header = "% tex_settings.txt\n\n% This is an auto-generated file, do not edit. Any necessary changes\n" + \
				"% should be made to the project.conf file.\n\n"

		# Pull in settings stored in the Process section of the project.conf object
		# As there are sub-sections we will add them to the settings object one
		# at after another. There's probably a better way to do this but not today ;-)
		settings = ""

		# First grab some individual settings we need to insert
#		cMapVal = self._log_manager._settings['General']['MapProcesses']['CREATE_MAP']
#		makefileSettings = makefileSettings + 'CREATE_MAP' + "=" + cMapVal + "\n"

		# Create the file footer (the things that go at the end)
		footer = "% Import custom project settings from secondary settings file.\n" + \
				"\\input ptx2pdf-setup.txt"

		# Output to the new makefile file
		settingsFileObject.write(header + settings + footer)
		settingsFileObject.close()


# This starts the whole process going
def doIt(log_manager):
	thisModule = MakeTexSettings()
	return thisModule.main(log_manager)
