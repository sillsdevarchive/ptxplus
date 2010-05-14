#!/usr/bin/python2.5
# -*- coding: utf-8 -*-
# version: 20100514
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This class will create the table of contents from ptx2pdf
# TeX output. It assumes:
#	1) Found in all rows are these markers: \tr \tc1 \tcr2
#	2) Output is to this format: \tbltwowlrow{BookName}{pg}
#
# Initial implementation is going to be pretty simple and
# will be built on as we go.

# History:
# 20100514 - djd - Initial draft


#############################################################
#################### Initialize The Process #################
#############################################################
# Firstly, import all the standard Python modules we need for
# this process

#import os, sys, codecs, csv, shutil, operator
import os, sys, codecs, shutil

# Import supporting local classes
#from tools import *
#tools = Tools()

class MakeTocFile (object) :

	# Intitate the whole class
	def __init__(self, log_manager) :

		self._settings = log_manager._settings
		self._log_manager = log_manager
		self._log_manager._currentSubProcess = 'MakeTocFile'
		self._texTocFile = log_manager._currentInput
		self._mainTitle = self._settings['Process']['TOC'].get('mainTitle','Table of Contents')
		self._columnFormat = self._settings['Process']['TOC'].get('columnFormat','twoColumnLeadered')
		self._bookID = log_manager._currentTargetID
		self._outputFile = log_manager._currentOutput
		self._outFileObject = {}




	def main(self):
		'''We will open up our content file which should be Unicode
			encoded and in SFM format. If that file doesn't exsist
			then we need to gracefully stop at that point. This will
			prevent other processes from crashing.'''

		if not os.path.isfile(self._texTocFile) :
			# If we don't have a SFM toc input file we're done now.
			self._log_manager.log("ERRR", "The [" + self._texTocFile + "] file does not exist so the process has been halted.")

		elif os.path.isfile(self._outputFile) :
			# If the output file exists we will not go through with the process
			# The user will need to manually verify and delete the file if
			# that is warrented before this process can be run again. This is
			# to prevent lost of work that may have been done to the TOC file.
			self._log_manager.log("INFO", "The " + self._outputFile + " exists so the process is being skipped.")

		else :

			# Everything is in place and we can move forward now

			# These tags are hard-coded tags and we are trying to repurpose the USFM
			# introduction tags. If there are conflicts between this and the introduction
			# texts we may need to introduce special new tags.
			USFMTags = ['\\imt1', '\\imt2', '\\imt3', '\\imi']
			# Creage header information for this sfm file
			headerInfo = "\\id OTH\n" + \
				"\\ide UTF-8\n" + \
				"\\periph " + self._bookID + "\n" + \
				"\\mt1 " + self._mainTitle + "\n" + \
				"\\p \n" + \
				"\\makedigitsother\catcode`{=1 \catcode`}=2\n" + \
				"\\baselineskip=12pt\n"


			# If we didn't bail out right above, we'll go ahead and open the data file
			# The assumption here is that the encoding of the pieces of the csv are
			# what they need to be.
#			csv_records = list(csv.reader(open(self._csvWorkFile), dialect=csv.excel))
			# Now we need output anything we might have collected. If nothing was
			# found, just output the header.
			self._outFileObject = codecs.open(self._outputFile, "w", encoding='utf_8_sig')
			self._outFileObject.write(headerInfo)
#			self._outFileObject.write(recordsToUSFM(USFMTags, csv_records))
#			self._log_manager.log("DBUG", "Created file and wrote out to: " + self._outputFile)

			# Close the piclist file
			self._outFileObject.close()

#			# Delete the temp CSV working file
#			if os.remove(self._csvWorkFile) == None :
#				self._log_manager.log("DBUG", "Removed file: " + self._csvWorkFile)



#def recordsToUSFM(tags, records) :
#	'''Process each field in a record and add an SFM tag to it.
#		if the field is empty do not output. Return a string.'''
#
#	usfm = []
#	for rec in records:
#		usfm.extend(map(lambda t,v: t + ' ' + v + '\n' if v else '', tags, rec))
#	# Turn the list into a string
#	return "".join(usfm)





# This starts the whole process going
def doIt(log_manager):

	thisModule = MakeTocFile(log_manager)
	return thisModule.main()
