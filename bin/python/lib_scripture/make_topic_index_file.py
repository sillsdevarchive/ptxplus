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
#	1) CSV 4 field input (section title, topic, sub topic, references)
#	2) Output to SFM (fixed markers)
#
# With these parameters met it will produce an SFM file that
# will need further processing, including possible encoding
# transformations, space and \n removal and editing.

# History:
# 20090506 - djd - Initial draft


#############################################################
#################### Initialize The Process #################
#############################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, sys, codecs, csv, shutil, operator

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
		self._csvWorkFile = os.getcwd() + "/" + self._settings['Process']['Paths']['PATH_TEXTS'] + "/zzz_TEMP.CSV"
		self._bookID = log_manager._currentTargetID
		self._outputFile = log_manager._currentOutput
		self._outFileObject = {}




	def main(self):
		'''We will open up our content file which should be Unicode
			encoded and in CSV format. If that file doesn't exsist
			then we need to gracefully stop at that point. This will
			prevent other processes from crashing.'''

		if not os.path.isfile(self._csvInputFile) :
			# If we don't have a CSV input file we're done now.
			self._log_manager.log("ERRR", "The [" + self._csvInputFile + "] file does not exist so the process has been halted.")

		elif os.path.isfile(self._outputFile) :
			# If the output file exists we will not go through with the process
			self._log_manager.log("INFO", "The " + self._outputFile + " exists so the process is being skipped.")

		else :

			# Copy over our CSV data so we can work with it
			# A simple file copy will do
			x = shutil.copy(self._csvInputFile, self._csvWorkFile)
			self._log_manager.log("DBUG", "The " + self._csvWorkFile + " has been copied from the Source folder.")

			# These tags are hard-coded tags and we are trying to repurpose the USFM
			# introduction tags. If there are conflicts between this and the introduction
			# texts we may need to introduce special new tags.
			USFMTags = ['\\imt1', '\\imt2', '\\imt3', '\\imi']
			# Creage header information for this sfm file
			headerInfo = "\\id OTH\n\\ide UTF-8\n\\periph Title Page\n\\mt1 <Title for Topical Index>\n"

			# If we didn't bail out right above, we'll go ahead and open the data file
			# The assumption here is that the encoding of the pieces of the csv are
			# what they need to be.
			csv_records = list(csv.reader(open(self._csvWorkFile), dialect=csv.excel))
			# Now we need output anything we might have collected. If nothing was
			# found, just output the header.
			self._outFileObject = codecs.open(self._outputFile, "w", encoding='utf-8')
			self._outFileObject.write(headerInfo)
			self._outFileObject.write(recordsToUSFM(USFMTags, csv_records))
			self._log_manager.log("DBUG", "Created file and wrote out to: " + self._outputFile)

			# Close the piclist file
			self._outFileObject.close()

			# Delete the temp CSV working file
			if os.remove(self._csvWorkFile) == None :
				self._log_manager.log("DBUG", "Removed file: " + self._csvWorkFile)



def recordsToUSFM(tags, records) :
	'''Process each field in a record and add an SFM tag to it.
		if the field is empty do not output. Return a string.'''

	usfm = []
	for rec in records:
		usfm.extend(map(lambda t,v: t + ' ' + v + '\n' if v else '', tags, rec))
	# Turn the list into a string
	return "".join(usfm)





# This starts the whole process going
def doIt(log_manager):

	thisModule = MakeTopicIndexFile(log_manager)
	return thisModule.main()
