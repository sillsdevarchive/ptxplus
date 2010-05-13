#!/usr/bin/python
# -*- coding: utf-8 -*-
# version: 20080423
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This script will auto-generate the system make file based
# on settings found in the project.cfg file. It does this
# every time the typeset file is used with valid commands.

# History:
# 20080806 - djd - Initial draft
# 20081023 - djd - Refactor project.conf structure changes
# 20081028 - djd - Removed system logging, messages only now
# 20090218 - djd - Added system logging access as other like
#		processes needed it too
# 20100513 - djd - Added key/value harvesting for Process::Files


#############################################################
######################### Load Modules ######################
#############################################################
# Firstly, import all the modules we need for this process

import sys, os, codecs

# Import supporting local classes
from tools import *
tools = Tools()


class MakeMakefile (object) :


	def main (self, log_manager) :
		'''This is the main process function for generating the makefile.'''

		self._log_manager = log_manager

		# Create the new makefile object (overwrite the old file)
		# Note here about encoding. If you use utf_8_sig rather than
		# just utf-8 it will put a BOM in the file. This seems to make
		# Make choke. Keeping with just utf-8 seems to fix it.
		makefileObject = codecs.open('Makefile', 'w', encoding='utf-8')

		# Create the file elements
		makefileHeader = "# Makefile\n\n# This is an auto-generated file, do not edit. Any necessary changes\n" + \
				"# should be made to the project.conf file.\n\n"

		# Pull in settings stored in the Process section of the project.conf object
		# As there are sub-sections we will add them to the settings object one
		# at after another. There's probably a better way to do this but not today ;-)
		makefileSettings = ""

		# First grab some individual settings we need in the makefile
		cMapVal = self._log_manager._settings['General']['MapProcesses']['CREATE_MAP']
		makefileSettings = makefileSettings + 'CREATE_MAP' + "=" + cMapVal + "\n"

		rgbPath = self._log_manager._settings['General']['MapProcesses']['RGB_PROFILE']
		makefileSettings = makefileSettings + 'RGB_PROFILE' + "=" + rgbPath + "\n"

		cmykPath = self._log_manager._settings['General']['MapProcesses']['CMYK_PROFILE']
		makefileSettings = makefileSettings + 'CMYK_PROFILE' + "=" + cmykPath + "\n"

		for key, value, in self._log_manager._settings['Process']['General'].iteritems() :
			makefileSettings = makefileSettings + key + "=" + value + "\n"

		for key, value, in self._log_manager._settings['Process']['Paths'].iteritems() :
			makefileSettings = makefileSettings + key + "=" + value + "\n"

		for key, value, in self._log_manager._settings['Process']['Files'].iteritems() :
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
				"include " + basePath + "/bin/make/matter_peripheral.mk\n" + \
				"include " + basePath + "/bin/make/matter_toc.mk\n" + \
				"include " + basePath + "/bin/make/matter_maps.mk\n" + \
				"include " + basePath + "/bin/make/system_hyphenation.mk\n" + \
				"include " + basePath + "/bin/make/system_files.mk\n"

		# Output to the new makefile file
		makefileObject.write(makefileHeader + makefileSettings + makefileFinal)


# This starts the whole process going
def doIt(log_manager):
	thisModule = MakeMakefile()
	return thisModule.main(log_manager)
