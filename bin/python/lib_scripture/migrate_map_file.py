#!/usr/bin/python2.5
# -*- coding: utf-8 -*-
# version: 20080622
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This class will migrate a map translation source file from
# the Source folder to the Maps folder so that it can be
# processed. If any encoding transformation tables are
# specified it will apply those as it copies the file to
# the Maps folder. Otherwise it will just do a simple copy.

# History:
# 20090508 - djd - Initial draft


#############################################################
#################### Initialize The Process #################
#############################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, sys, codecs, csv, shutil

# Import supporting local classes
from tools import *
tools = Tools()

class MigrateMapFile (object) :

	# Intitate the whole class
	def __init__(self, log_manager) :

		self._settings = log_manager._settings
		self._log_manager = log_manager
		self._log_manager._currentSubProcess = 'MigrateMapFile'
		self._inputFile = log_manager._currentInput
		self._bookID = log_manager._currentTargetID
		self._outputFile = log_manager._currentOutput
		self._outFileObject = {}
#		self._sourcePath = os.getcwd() + "/" + self._settings['Process']['Paths']['PATH_SOURCE']


	def main(self):
		'''We will open up our project translation file which should be
			Unicode encoded and in CSV format. If that file doesn't exsist
			then we need to gracefully stop at that point. This will
			prevent other processes from crashing.'''

		#if os.path.isfile(self._outputFile) :
			## If the project map csv file exists we will not go through with the process
			#self._log_manager.log("INFO", "The " + self._outputFile + " exists so the process is being halted.")

		#else :

		# Otherwise we will create a new project map csv file
		# Assumption: If encoding chain exists, we process
		chain = self._settings['Encoding']['Processing']['encodingChain']
		if chain != "" :
			mod = __import__("transformCSV")
			# We'll give the source, target, encoding chain and field to transform
			# Remember that the field count starts at 0
			res = mod.doIt(self._inputFile, self._outputFile, chain, 1)
			if res != None :
				self._log_manager.log("ERRR", res)
				return
			else :
				self._log_manager.log("INFO", "The " + self._outputFile + " has been copied from the Maps folder with an encoding tranformation on the caption field.")

		# If there is no encoding chain a simple file copy will do
		else :
			x = shutil.copy(self._inputFile, self._outputFile)
			self._log_manager.log("INFO", "The " + self._outputFile + " has been copied from the Maps folder.")


# This starts the whole process going
def doIt(log_manager):

	thisModule = MigrateMapFile(log_manager)
	return thisModule.main()
