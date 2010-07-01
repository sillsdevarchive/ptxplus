#!/usr/bin/python2.5
# -*- coding: utf_8 -*-
# version: 20080423
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This script will auto-generate the system make file based
# on settings found in the .scripture.cfg file. It does this
# every time the typeset file is used with valid commands.

# History:
# 20080806 - djd - Initial draft
# 20081023 - djd - Refactor .project.conf structure changes
# 20081028 - djd - Removed system logging, messages only now
# 20090218 - djd - Added system logging access as other like
#        processes needed it too
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

		# The folder name for peripheral material is auto created here
		peripheralFolderName = os.getcwd().split('/')[-1]

		# Create the new makefile object (overwrite the old file)
		# Note here about encoding. If you use utf_8_sig rather than
		# just utf_8 it will put a BOM in the file. This seems to make
		# Make choke. Keeping with just utf_8 seems to fix it.
		makefileObject = codecs.open('.makefile', 'w', encoding='utf_8')

		# Create the file elements
		makefileHeader = "# Makefile\n\n# This is an auto-generated file, do not edit. Any necessary changes\n" + \
				"# should be made to the .scripture.conf file.\n\n"

		# Pull in settings stored in the Process section of the .scripture.conf object
		# As there are sub-sections we will add them to the settings object one
		# at after another. There's probably a better way to do this but not today ;-)
		makefileSettings = ""

		# First grab some individual settings we need in the makefile
		cMapVal = self._log_manager._settings['System']['Processes']['MapProcesses'].get('CREATE_MAP',0)
		makefileSettings = makefileSettings + 'CREATE_MAP' + "=" + cMapVal + "\n"

		rgbPath = self._log_manager._settings['System']['Processes']['MapProcesses'].get('RGB_PROFILE','/usr/share/color/icc/sRGB.icm')
		makefileSettings = makefileSettings + 'RGB_PROFILE' + "=" + rgbPath + "\n"

		cmykPath = self._log_manager._settings['System']['Processes']['MapProcesses'].get('CMYK_PROFILE','/usr/share/color/icc/ISOcoated.icc')
		makefileSettings = makefileSettings + 'CMYK_PROFILE' + "=" + cmykPath + "\n"

		# Modules used by the makefile, note the use of extra
		# quoting. This is to preserve the strings.
		for key, value, in self._log_manager._settings['System']['Modules'].iteritems() :
			makefileSettings = makefileSettings + key + "=\"" + value + "\"\n"

		for key, value, in self._log_manager._settings['Format']['PageLayout']['Switches'].iteritems() :
			makefileSettings = makefileSettings + key + "=" + value + "\n"

		for key, value, in self._log_manager._settings['ProjectText']['SourceText']['General'].iteritems() :
			makefileSettings = makefileSettings + key + "=" + value + "\n"

		for key, value, in self._log_manager._settings['System']['Extensions'].iteritems() :
			makefileSettings = makefileSettings + key + "=" + value + "\n"

		for key, value, in self._log_manager._settings['System']['Paths'].iteritems() :
			makefileSettings = makefileSettings + key + "=" + value + "\n"

		# Insert the peripheral folder name here. This is a
		# hard-coded insert because it should always be the
		# name given here. The user cannot change this.
		makefileSettings = makefileSettings + 'PATH_SOURCE_PERIPH' + "=" + peripheralFolderName + "\n"

		for key, value, in self._log_manager._settings['System']['Files'].iteritems() :
			makefileSettings = makefileSettings + key + "=" + value + "\n"

		for key, value, in self._log_manager._settings['System']['TeX'].iteritems() :
			makefileSettings = makefileSettings + key + "=" + value + "\n"

		for key, value, in self._log_manager._settings['Format']['Binding'].iteritems() :
			makefileSettings = makefileSettings + key + "=" + value + "\n"

		for key, value, in self._log_manager._settings['System']['HelperCommands'].iteritems() :
			makefileSettings = makefileSettings + key + "=" + value + "\n"


		# Add make rule files via the include call in make
		# This is all controled via the .scripture.conf file
		basePath = os.environ.get('PTXPLUS_BASE')
		makefileFinal = "include " + basePath + "/bin/make/" + self._log_manager._settings['System']['MakefileSettings']['MakeIncludeVariables'][self._log_manager._settings['ProjectText']['SourceText']['General']['projectEditor']] + "\n"

		for key, value, in self._log_manager._settings['System']['MakefileSettings']['MakeInclude'].iteritems() :
			makefileFinal = makefileFinal + "include " + basePath + "/bin/make/" + value + "\n"

		# Output to the new makefile file
		makefileObject.write(makefileHeader + makefileSettings + makefileFinal)

# This starts the whole process going
def doIt(log_manager):
	thisModule = MakeMakefile()
	return thisModule.main(log_manager)
