#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20100126
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This script will create a USFM file that contains all the
# publication information for the current project. It is
# intended to be typeset and included with the archive and
# PR distribution copies

# History:
# 20100126 - djd - Initial draft


#############################################################
######################### Load Modules ######################
#############################################################
# Firstly, import all the modules we need for this process

import sys, os, codecs

# Import supporting local classes
from tools import *
tools = Tools()
from configobj import ConfigObj


class MakeProjectInfo (object) :

	def __init__(self, log_manager):
		self._log_manager = log_manager
		self._inputFile = log_manager._currentInput
		self._config = ConfigObj('project.conf',encoding="utf-8")

	def main (self) :
		'''This is the main process function for generating the file.'''

		# Set a couple vars here
		projectInfo = ""

		# Create the new makefile object (overwrite the old file if needed)
		fileObject = codecs.open(self._inputFile, 'w', encoding='utf_8')

		# Insert the basic SFMs for this file
		fileHeader = "\\id OTH\n\\ide UTF-8\n\\periph Project Info\n\\mt1 Project Information\n\n"

#        projectInfo = self._config['General']['ProjectInformation'].get('projectName')
#        for i in self._config['General']['ProjectInformation'].inline_comments.iteritems() :
#            projectInfo = projectInfo + '\\li Description: ' + i + '\n'

		# Insert the project data
		for key, value, in self._log_manager._settings['General']['ProjectInformation'].iteritems() :
			comment = self._log_manager._settings['General']['ProjectInformation'].comments[key]
			comment = comment[1].replace('# ', '')
			projectInfo = projectInfo + '\\li ' + comment + ': \\hfill ' + value + '\n'


#        projectInfo = self._config['General']['ProjectInformation']['copyrightYear'].comments


		# Output to the new makefile file
		fileObject.write(fileHeader + projectInfo)

		fileObject.close()


	def stuff (self) :

		# A simple place holder for stuff not used yet

		# Create the file elements
		makefileHeader = "# Makefile\n\n# This is an auto-generated file, do not edit. Any necessary changes\n" + \
				"# should be made to the project.conf file.\n\n"

		# Pull in settings stored in the Process section of the project.conf object
		# As there are sub-sections we will add them to the settings object one
		# at after another. There's probably a better way to do this but not today ;-)
		makefileSettings = ""
		for key, value, in self._log_manager._settings['Process']['General'].iteritems() :
			makefileSettings = makefileSettings + key + "=" + value + "\n"

		for key, value, in self._log_manager._settings['Process']['Paths'].iteritems() :
			makefileSettings = makefileSettings + key + "=" + value + "\n"

		for key, value, in self._log_manager._settings['Process']['TeX'].iteritems() :
			makefileSettings = makefileSettings + key + "=" + value + "\n"

		for key, value, in self._log_manager._settings['Process']['Binding'].iteritems() :
			makefileSettings = makefileSettings + key + "=" + value + "\n"

		for key, value, in self._log_manager._settings['Process']['HelperCommands'].iteritems() :
			makefileSettings = makefileSettings + key + "=" + value + "\n"

		editorBibleInfo = ""

		# Add rules from the system that are not in the .conf files
		# The order of the include is important. We include system_files.mk last
		# so that all of the other rules are caught and can be expanded in that
		# make file.
		basePath = os.environ.get('PTXPLUS_BASE')
		if self._log_manager._settings['General']['projectEditor'] == 'ptx' :
			editorBibleInfo = "include " + basePath + "/bin/make/ptx_bible_info.mk\n"
		elif self._log_manager._settings['General']['projectEditor'] == 'be' :
			editorBibleInfo = "include " + basePath + "/bin/make/be_bible_info.mk\n"
		elif self._log_manager._settings['General']['projectEditor'] == 'te' :
			editorBibleInfo = "include " + basePath + "/bin/make/te_bible_info.mk\n"

		makefileFinal = "include " + basePath + "/bin/make/common_bible_info.mk\n" + \
				editorBibleInfo + \
				"include " + basePath + "/bin/make/periph_info.mk\n" + \
				"include " + basePath + "/bin/make/matter_books.mk\n" + \
				"include " + basePath + "/bin/make/matter_maps.mk\n" + \
				"include " + basePath + "/bin/make/matter_peripheral.mk\n" + \
				"include " + basePath + "/bin/make/system_files.mk\n"

		# Output to the new makefile file
		makefileObject.write(makefileHeader + makefileSettings + makefileFinal)


# This starts the whole process going
def doIt(log_manager):

	thisModule = MakeProjectInfo(log_manager)
	return thisModule.main()
