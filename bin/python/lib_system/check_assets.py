#!/usr/bin/python2
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
#
# There is also a fallback location. If it doesn't find the
# file it needs in the default location it will fall back to
# the system lib where some of the necessary files exist.
# If it doesn't find it there it will throw an additional
# error.

# History:
# 20100707 - djd - Initial draft


#############################################################
######################### Load Modules ######################
#############################################################
# Firstly, import all the modules we need for this process

import sys, os, shutil

import tools

class CheckAssets (object) :


	def main (self, log_manager) :
		'''This is the main process function for getting and checking
			project assets.'''

		tools.userMessage('INFO: Checking project assets')
		# Set the mode
		self._log_manager = log_manager
		self._mode = self._log_manager._optionalPassedVariable
		if self._mode == '' :
			self._mode = 'basic'

		# Gather up the initial settings
		basePath                = os.environ.get('PTXPLUS_BASE')
		pathHome                = os.path.abspath(tools.pubInfoObject['Paths']['PATH_HOME'])
		pathHyphenation         = pathHome + '/' + tools.pubInfoObject['Paths']['PATH_HYPHENATION']
		pathProcess             = pathHome + '/' + tools.pubInfoObject['Paths']['PATH_PROCESS']
		pathSource              = os.path.abspath(tools.pubInfoObject['Paths']['PATH_SOURCE'])
		pathPeripheral          = pathSource + '/' + os.getcwd().split('/')[-1]
		pathMaps                = pathPeripheral + '/Maps'
		pathIllustrations       = os.path.abspath(tools.pubInfoObject['Paths']['PATH_ILLUSTRATIONS'])
		pathGraphics            = os.path.abspath(self._log_manager._settings['System']['Paths']['PATH_GRAPHICS_LIB'])
		pathIllustrationsLib    = tools.pubInfoObject['Paths']['PATH_RESOURCES_ILLUSTRATIONS'].replace('__PTXPLUS__', basePath)
		fileWatermark           = self._log_manager._settings['Format']['PageLayout']['FILE_WATERMARK']
		filePageBorder          = self._log_manager._settings['Format']['PageLayout']['FILE_PAGE_BORDER']
		listGraphics            = self._log_manager._settings['Format']['Illustrations']['LIST_GRAPHICS']

		# Do some sanity testing
		if not os.path.isdir(pathGraphics) :
			self._log_manager.log('ERRR', 'No graphics source folder. (Halting) Please check your configuration.', 'true')
			sys.exit(1)

		# Check/install folders we might need
		if not os.path.isdir(pathSource) :
			os.mkdir(pathSource)
			self._log_manager.log('INFO', 'Added folder: ' + pathSource, 'true')

		if not os.path.isdir(pathPeripheral) :
			os.mkdir(pathPeripheral)
			self._log_manager.log('INFO', 'Added folder: ' + pathPeripheral, 'true')

		if not os.path.isdir(pathMaps) :
			os.mkdir(pathMaps)
			self._log_manager.log('INFO', 'Added folder: ' + pathMaps, 'true')

		if not os.path.isdir(pathIllustrations) :
			os.mkdir(pathIllustrations)
			self._log_manager.log('INFO', 'Added folder: ' + pathIllustrations, 'true')

		if not os.path.isdir(pathHyphenation) :
			os.mkdir(pathHyphenation)
			self._log_manager.log('INFO', 'Added folder: ' + pathHyphenation, 'true')

		if not os.path.isdir(pathProcess) :
			os.mkdir(pathProcess)
			self._log_manager.log('INFO', 'Added folder: ' + pathProcess, 'true')


		# Check/install system assets

		# Watermark
		self.smartCopy(pathGraphics + '/' + fileWatermark, pathIllustrations + '/' + fileWatermark, pathProcess + '/' + fileWatermark, pathIllustrationsLib + '/' + fileWatermark)
		# Page border
		self.smartCopy(pathGraphics + '/' + filePageBorder, pathIllustrations + '/' + filePageBorder, pathProcess + '/' + filePageBorder, pathIllustrationsLib + '/' + filePageBorder)
		# Graphics list
		for graphic in listGraphics :
			self.smartCopy(pathGraphics + '/' + graphic, pathIllustrations + '/' + graphic, pathProcess + '/' + graphic, pathIllustrationsLib + '/' + graphic)

	def smartCopy (self, source, destination, linkto, lib) :
		'''Copies a file but does it according to the mode the
			script is in.'''

		if self._mode == 'basic' :
			if os.path.isfile(destination) :
				self._log_manager.log("INFO", "Mode = " + self._mode + " The file: [" + destination + "] is already there. Nothing to do.")
				# But what if there is no link, better check
				self.justLink(destination, linkto)
			else :
				self.copyLink(source, destination, linkto, lib)
		elif self._mode == 'refresh' :
				self.copyLink(source, destination, linkto, lib)
		else :
				self._log_manager.log('ERRR', 'Mode [' + self._mode + '] is not supported. Cannot complete!', 'true')


	def copyLink (self, source, destination, linkto, lib) :
		'''Copy and link a given file. If not found, look in the
			system resouce lib.'''

		if os.path.isfile(source) :
			shutil.copy(source, destination)
			if os.path.isfile(destination) :
				self._log_manager.log("INFO", "Mode = " + self._mode + " The file: [" + source + "] has been copied to: [" + destination + "]")
				self.justLink(destination, linkto)
			else :
				self._log_manager.log("ERRR", "Failed to copy: " + destination + " Process incomplete.", 'true')
		else :
			if os.path.isfile(lib) :
				shutil.copy(lib, destination)
				self._log_manager.log("INFO", "File: " + destination + " had to be copied from the system lib.")
				self.justLink(destination, linkto)
			else :
				self._log_manager.log("ERRR", "Not found: " + destination + " Process incomplete.", 'true')


	def justLink (self, destination, linkto) :
		'''Just check to see if a link is needed into the project.'''

		if not os.path.isfile(linkto) :
			os.symlink(destination, linkto)
			if os.path.isfile(linkto) :
				self._log_manager.log("INFO", "Mode = " + self._mode + " The file: [" + destination + "] has been linked to: [" + linkto + "]")
			else :
				self._log_manager.log("ERRR", "Mode = " + self._mode + " File: [" + linkto + "] not linked.", 'true')


# This starts the whole process going
def doIt(log_manager):

	thisModule = CheckAssets()
	return thisModule.main(log_manager)

