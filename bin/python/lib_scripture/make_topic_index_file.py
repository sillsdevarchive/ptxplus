#!/usr/bin/python2.5
# -*- coding: utf-8 -*-
# version: 20080622
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This class will create the contents for a basic topical
# index. It assumes:
#	1) CSV input (section title, topic, sub topic, references)
#	2) Output to SFM (fixed markers)
#
# With these parameters met it will produce an SFM file that
# will need further editing.

# History:
# 20090506 - djd - Initial draft


#############################################################
#################### Initialize The Process #################
#############################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, sys, codecs, csv, shutil

# Import supporting local classes
from encoding_manager import *
from tools import *
tools = Tools()

class MakeTopicIndexFile (object) :

	# Intitate the whole class
	def __init__(self, log_manager) :

		self._settings = log_manager._settings
		self._log_manager = log_manager
		self._log_manager._currentSubProcess = 'MakeTopicIndexFile'
		self._csvInputFile = log_manager._currentInput
		self._csvWorkFile = os.getcwd() + "/" + self._settings['Process']['Paths']['PATH_PERIPH'] + "/zzz_TEMP.CSV"
		self._bookID = log_manager._currentTargetID
		self._outputFile = log_manager._currentOutput
		self._outFileObject = {}




	def main(self):
		'''We will open up our content file which should be Unicode
			encoded and in CSV format. If that file doesn't exsist
			then we need to gracefully stop at that point. This will
			prevent other processes from crashing.'''

		if os.path.isfile(self._outputFile) :
			# If the output file exists we will not go through with the process
			self._log_manager.log("INFO", "The " + self._outputFile + " exists so the process is being halted.")

		elif not os.path.isfile(self._csvInputFile) :
			# If we don't have a CSV input file we're done now.
			self._log_manager.log("ERRR", "The [" + self._csvInputFile + "] file does not exist so the process has been halted.")

		else :

# here we will go directly to the TxtconvChain module to do the work.
# we don't need to do any individual fields, just push the whole file
# this is the code we should need (needs mods)

		# Initialize the encoder
		encodingChain = TxtconvChain([s.strip() for s in encodingChain.split(',')])
		# Re-encode the data
		newFieldData = encodingChain.convert(fieldData).split('\n')




			# Copy over our CSV data so we can work with it
			# Assumption: If encoding chain exists, we process
			chain = self._settings['Encoding']['Processing']['encodingChain']
			if chain != "" :
				mod = __import__("transformCSV")
				# We'll give the source, target, encoding chain and field to transform
				res = mod.doIt(self._csvInputFile, self._csvWorkFile, chain, 1)
				if res != None :
					self._log_manager.log("ERRR", res)
					return
				else :
					self._log_manager.log("INFO", "The " + self._csvWorkFile + " has been copied from the Source folder with encoding tranformation on all fields.")

			# If there is no encoding chain a simple file copy will do
			else :
				x = shutil.copy(self._csvInputFile, self._csvWorkFile)
				self._log_manager.log("INFO", "The " + self._csvMasterFile + " has been copied from the Source folder.")


			# If we didn't bail out right above, we'll go ahead and open the data file
			# The assumption here is that the encoding of the pieces of the csv are
			# what they need to be.
			inFileData = csv.reader(open(self._csvWorkFile), dialect=csv.excel)

			for line in inFileData :
				self._outFileObject = line[4]

			# Now we need output anything we might have collected. If nothing was
			# found, just an empty file will be put out.
			self._outFileObject = codecs.open(self._outputFile, "w", encoding='utf-8')
			self._log_manager.log("DBUG", "Created file: " + self._outputFile)
			for line in self._piclistData :
				self._outFileObject.write(line + "\n")

			# Close the piclist file
			self._outFileObject.close()

			# Delete the temp CSV working file

			# Tell the world what we did
			self._log_manager.log("INFO", "Process complete")



# This starts the whole process going
def doIt(log_manager):

	thisModule = MakeTopicIndexFile(log_manager)
	return thisModule.main()
