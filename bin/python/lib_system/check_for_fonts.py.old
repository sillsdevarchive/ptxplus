#!/usr/bin/python2
# -*- coding: utf_8 -*-
# version: 20080423
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This script will check for fonts in a project and try to
# import them from the _resources folder if the project
# doesn't have them. This is fairly simple right now but
# may need to be expanded as needs grow.

# History:
# 20080819 - djd - Initial draft
# 20081028 - djd - Removed system logging, messages only now
# 20090218 - djd - Readded system logging access as some
#        other processes need it


#############################################################
######################### Load Modules ######################
#############################################################
# Firstly, import all the modules we need for this process

from font_manager import *
import tools
font_manager = FontManager()

class CheckForFonts (object) :


	def main (self, log_manager) :
		'''This is the main process function for generating the makefile.'''

		self._log_manager = log_manager

		# Check to see if the right fonts are in the project. Put them
		# there if not and if that fails, throw an error
		if font_manager.haveFonts() == False :
			if font_manager.installFonts() == False :
				tools.userMessage('The specified font family (' + font_manager.projectFontFamily + ') could not be installed. (Maybe it is not in the folder?)')
			else :
				tools.userMessage('Project fonts had to be installed. Installation was successful.')


# This starts the whole process going
def doIt(log_manager):

	thisModule = CheckForFonts()
	return thisModule.main(log_manager)

