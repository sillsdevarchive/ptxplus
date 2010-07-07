#!/usr/bin/python2.5
# -*- coding: utf_8 -*-
# version: 20100707
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This script will check for project assets such as graphics
# and other kinds of files listed in the .conf file. The
# script has two basic modes. The basic mode will look for
# the files and copy them into the location the .conf file
# says it should. If the file is already there, it will NOT
# overwrite it. In the refresh mode, it will copy over any
# existing files that are there with the ones if finds in
# the source area it was directed to.

# History:
# 20100707 - djd - Initial draft


#############################################################
######################### Load Modules ######################
#############################################################
# Firstly, import all the modules we need for this process

import sys, os, shutil

from tools import *
tools = Tools()

class CheckAssets (object) :


	def main (self, log_manager) :
		'''This is the main process function for getting and checking
			project assets.'''

		# Set the mode
		self._log_manager = log_manager
		self._mode = self._log_manager._optionalPassedVariable
		if self._mode == '' :
			self._mode = 'basic'

		# Gather up the initial settings
		pathHome            = os.path.abspath(self._log_manager._settings['System']['Paths']['PATH_HOME'])
		pathSource          = os.path.abspath(self._log_manager._settings['System']['Paths']['PATH_SOURCE'])
		pathProcess         = pathHome + '/' + self._log_manager._settings['System']['Paths']['PATH_PROCESS']
		pathIllustrations   = os.path.abspath(self._log_manager._settings['System']['Paths']['PATH_ILLUSTRATIONS'])
		pathGraphics        = os.path.abspath(self._log_manager._settings['System']['Paths']['PATH_GRAPHICS_LIB'])
		fileWatermark       = self._log_manager._settings['System']['Files']['FILE_WATERMARK']
		filePageBorder      = self._log_manager._settings['System']['Files']['FILE_PAGE_BORDER']
		listGraphics        = self._log_manager._settings['Format']['Illustrations']['LIST_GRAPHICS']

		# Do some sanity testing
		if pathGraphics == '' :
			tools.userMessage('ERROR: check your configuration, no setting for the graphics source path found. Halting process now!')
			self._log_manager.log('ERRR', 'There is no setting for the graphics source path. Please check your configuration.')
			sys.exit(1)

		# Check/install folders we might need
		if not os.path.isdir(pathIllustrations) :
			os.mkdir(pathIllustrations)
			tools.userMessage('INFO: Added folder: ' + pathIllustrations)

		# Check/install system assets

		# Watermark
		self.smartCopy(pathGraphics + '/' + fileWatermark, pathIllustrations + '/' + fileWatermark, pathProcess + '/' + fileWatermark)
		# Page border
		self.smartCopy(pathGraphics + '/' + filePageBorder, pathIllustrations + '/' + filePageBorder, pathProcess + '/' + filePageBorder)
		# Graphics list
		for graphic in listGraphics :
			self.smartCopy(pathGraphics + '/' + graphic, pathIllustrations + '/' + graphic, pathProcess + '/' + graphic)

	def smartCopy (self, source, destination, linkto) :
		'''Copies a file but does it according to the mode the
			script is in.'''

		if self._mode == 'basic' :
			if os.path.isfile(destination) :
				self._log_manager.log("INFO", "Mode = " + self._mode + " The file: [" + destination + "] is already there. Nothing to do.")
			else :
				self.copyLink(source, destination, linkto)
		elif self._mode == 'refresh' :
				self.copyLink(source, destination, linkto)
		else :
				self._log_manager.log('ERRR', 'Mode [' + self._mode + '] is not currently supported by the system. Cannot complete operation.')
				tools.userMessage('ERROR: Mode [' + self._mode + '] is not currently supported by the system. Cannot complete operation.')


	def copyLink (self, source, destination, linkto) :
		'''Don't be creative, just copy and link a given file.'''

		shutil.copy(source, destination)
		self._log_manager.log("INFO", "Mode = " + self._mode + " The file: [" + source + "] has been copied to: [" + destination + "]")
		if not os.path.isfile(linkto) :
			os.symlink(destination, linkto)
			self._log_manager.log("INFO", "Mode = " + self._mode + " The file: [" + destination + "] has been linked to: [" + linkto + "]")


# This starts the whole process going
def doIt(log_manager):

	thisModule = CheckAssets()
	return thisModule.main(log_manager)
