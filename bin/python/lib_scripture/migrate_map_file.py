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
		self._outputFile = self._currentOutput
		self._outFileObject = {}
#		self._sourcePath = os.getcwd() + "/" + self._settings['Process']['Paths']['PATH_SOURCE']


	def main(self):
		'''We will open up our project translation file which should be
			Unicode encoded and in CSV format. If that file doesn't exsist
			then we need to gracefully stop at that point. This will
			prevent other processes from crashing.'''


# Start up here fixing this file



		if os.path.isfile(self._outputFile) :
			# If the book piclist exists we will not go through with the process
			self._log_manager.log("INFO", "The " + self._outputFile + " exists so the process is being halted.")

		elif tools.isPeripheralMatter(self._inputFile) :
			# If the file belongs to the peripheral mater we will not go through with the process
			self._log_manager.log("INFO", "The " + self._inputFile + " is part of the peripheral mater so the process is being halted.")

		else :
			# Otherwise we will create a new book piclist file
			if not os.path.isfile(self._csvMasterFile) :
				# If it doesn't exist that isn't necessarily a problem.
				# First we'll go look for a source file and if we find it
				# we'll copy it into the Illustrations folder and process
				# it as needed. If we don't find one we'll just output
				# a warning to the log and exit gracefully.

				# Is there a source file of the same name in the Source folder?
				if os.path.isfile(self._csvSourceFile) :
					# Assumption: If encoding chain exists, we process
					chain = self._settings['Encoding']['Processing']['encodingChain']
					if chain != "" :
						mod = __import__("transformCSV")
						# We'll give the source, target, encoding chain and field to transform
						res = mod.doIt(self._csvSourceFile, self._csvMasterFile, chain, 8)
						if res != None :
							self._log_manager.log("ERRR", res)
							return
						else :
							self._log_manager.log("INFO", "The " + self._csvMasterFile + " has been copied from the Source folder with an encoding tranformation on the caption field.")

					# If there is no encoding chain a simple file copy will do
					else :
						x = shutil.copy(self._csvSourceFile, self._csvMasterFile)
						self._log_manager.log("INFO", "The " + self._csvMasterFile + " has been copied from the Source folder.")


			# If we didn't bail out right above, we'll go ahead and open the data file
			# The assumption here is that the encoding of the pieces of the csv are
			# what they need to be.
			inFileData = csv.reader(open(self._csvMasterFile), dialect=csv.excel)

			# Right here we will sort the list by BCV. This should prevent unsorted
			# data from getting out into the piclist. First change the data to a list.
			masterData = []
			for line in inFileData :
				masterData.append(line)

			# This will sort it
			masterData.sort(cmp=lambda x,y: cmp(x[1],y[1]) or cmp(int(x[2]),int(y[2])) or cmp(int(x[3]),int(y[3])))

			pics = 0
			for line in masterData :
				# Throw out the header line (there should be one!)
				#if pics == 0 :
					#pics +=1
					#continue
				#else :
				if self._bookID == line[1] :
					# Now we'll write out what we've found
					# More error correction needs to go here
					# I would think but this will be ok to
					# start with.
					self.collectPicLine(line[0].upper(), line[1].upper(), line[2], line[3], \
					line[4], \
					line[5], line[6], line[8])
					self.processIllustration(line[4])
					pics +=1

			# Now we need output anything we might have collected. If nothing was
			# found, just an empty file will be put out.
			self._outFileObject = codecs.open(self._outputFile, "w", encoding='utf-8')
			self._log_manager.log("DBUG", "Created file: " + self._outputFile)
			for line in self._piclistData :
				self._outFileObject.write(line + "\n")

			# Close the piclist file
			self._outFileObject.close()

			# Tell the world what we did
			self._log_manager.log("INFO", "We processed " + str(pics-1) + " illustration line(s) for: " + self._bookID)



# This starts the whole process going
def doIt(log_manager):

	thisModule = MigrateMapFile(log_manager)
	return thisModule.main()
