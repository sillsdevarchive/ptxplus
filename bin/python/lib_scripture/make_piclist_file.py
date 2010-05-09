#!/usr/bin/python2.5
# -*- coding: utf-8 -*-
# version: 20080622
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This class will create a picture listing file for a
# Bible book being processed with the pdf2ptx macro set
# in XeTeX.

# History:
# 20080623 - djd - Initial draft
# 20080904 - djd - Changed to output .piclist file even if
#		there are no pictures to process. This solves
#		a dependency problem in makefile
# 20081023 - djd - Refactored due to changes in project.conf
# 20081030 - djd - Added total dependence on log_manager.
#		This script will not run without it because
#		it handles all the parameters it needs.
# 20081230 - djd - Changed over to work stand-alone instead
#		of through version control.
# 20090504 - djd - Added a filter for peripheral matter files
# 20091214 - djd - Added a check for missing lib info. If not
#		found then it is reported and the process is
#		halted.
# 20100414 - djd - Changed the way process works by adding a
#		lib data file and limiting the project file to
#		only containing caption and location info.


#############################################################
#################### Initialize The Process #################
#############################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, sys, codecs, csv, shutil, pdb
from operator import itemgetter

# Import supporting local classes
from tools import *
tools = Tools()


class MakePiclistFile (object) :
	'''This class will create a .piclist file from a captions and data file for
		a set of illustrations.'''

	def __init__(self, log_manager) :
		'''Intitate everything we need for this class here.'''

		self._settings = log_manager._settings
		self._log_manager = log_manager
		self._log_manager._currentSubProcess = 'MakePiclistFile'
		self._bookID = log_manager._currentTargetID

		# Pull in some default sizing params if they exist, if not use the default settings.
		self._texsize = self._settings['General']['Resources']['Illustrations'].get('size','col')
		self._texpos = self._settings['General']['Resources']['Illustrations'].get('position','tl')
		self._texscale = self._settings['General']['Resources']['Illustrations'].get('scale',1.0)
		self._inputFile = log_manager._currentInput
		self._outputFile = self._inputFile + ".piclist"
		self._outFileObject = {}
		self._sourcePath = self._settings['Process']['Paths']['PATH_SOURCE']

# Need to work here and figure out what happens in this script and the makefile

		self._sharedIllustrationsPath = self._sourcePath + "/" + self._settings['Process']['Paths']['PATH_ILLUSTRATIONS_SHARED']
		self._processIllustrationsPath = os.getcwd() + "/" + self._settings['Process']['Paths']['PATH_ILLUSTRATIONS']
		self._sourceIllustrationsLibPath = self._settings['Process']['Paths']['PATH_ILLUSTRATIONS_LIB']
		(head, tail) = os.path.split(self._sourceIllustrationsLibPath)
		self._sourceIllustrationsLibData = self._sourceIllustrationsLibPath + "/" + tail + "_data.csv"
		self._sourceIllustrationsCaptions = self._sourcePath + "/captions.csv"
		self._projectIllustrationsCaptions = self._processIllustrationsPath + "/captions.csv"

		# Pull in the library data file using the CSVtoDict class in tools
		self._libData = CSVtoDict(self._sourceIllustrationsLibData)
#		self._libData = CSVtoDict('/home/dennis/Publishing/_resources/lib_illustrations/Knowles-600/Knowles-data.csv')

		self._errors = 0


	def collectPicLine (self, illID, bookID, chapNum, verseNum, eCap, vCap) :
		'''Collect and format an illustration description line. The incoming
			file will not have all the information we need so we'll get
			some things from the illustration lib. The output format goes
			like this:
				bid_c.v_|fileName|size (col/span)|location (b/t+l/r)|scale (1.0)|Copyright|Caption|ref

			Note the space after the v, that needs to be there or TeX
			will choke. In the incoming arguments, the caption field
			"eCap" contains the English version of the caption. Next
			to that goes the translation field "vCap" which holds the
			vernacular version of the caption field.'''

		# Build the cv ref
		ref = chapNum + "." + verseNum

		# Get the file name from the illustration data
		def_fileName = "FILE NAME MISSING!"
		fileName = self._libData[illID].get('FileName', def_fileName)

		# Get the copyright information from the illustration data
		def_copyright = "COPYRIGHT INFORMATION IS MISSING!"
		copyright = self._libData[illID].get('Copyright', def_copyright)

		# Build the caption
		caption = eCap
		if vCap != "" :
			caption = vCap

		line = bookID + " " + ref + " |" + fileName + "|" + self._texsize + "|" + self._texpos + "|" + \
				str(self._texscale) + "|" + copyright + "|" + caption + "|" + ref
		self._log_manager.log("DBUG", "Collected: " + line)

		# We're done return the results
		return line


	def processIllustrationFile (self, illID) :
		'''This is just a generalized illustration processing function.
			The file name is pulled from the libData dictionary.
			If that fails, this all falls apart and an error is given.
			It will handle copying and linking processes for a
			single illustration file. The source comes from a
			resource lib that is present in the system. The target
			file is in the source folder so it can be shared across
			projects. The link file is located in the Illustrations
			folder and points back to the shared folder in the
			source area.'''

		# Get the file name from the illustration data
		def_fileName = "FILE NAME MISSING!"
		fileName = self._libData[illID].get('FileName', def_fileName)

		# Build the file names
		source = self._sourceIllustrationsLibPath + "/" + fileName
		target = self._sharedIllustrationsPath + "/" + fileName
		link = self._processIllustrationsPath + "/" + fileName

		# Sanity test
		if not os.path.isfile(source) :
			self._log_manager.log("ERRR", "The file: " + source + " was not found.")
		# Check to see if the file is there or not. We don't want to copy
		# one in if one exists already.
		if not os.path.isfile(target) :
			# Copy the picture file from the source to the target location
			shutil.copy(source, target)
			self._log_manager.log("DBUG", "Copied from: " + source + " ---To:--> " + target)
			# Use os.symlink(source, link_name) to make a symbolic link
			# from the target to the Illstrations folder we will do
			# that every time an illustration is copied into the
			# shared folder.
			if not os.symlink(target, link) :
				self._log_manager.log("ERRR", "The file: " + target + " could not be linked to: " + link)


	def main(self):
		'''We will open up our captions file which should be Unicode
			encoded and in CSV format. The illustration IDs will
			be matched from that file with the lib data file and
			will create a piclist file for the book that is
			currently being processed.'''

		# Before we start we need to be sure our init succeeded so
		# we will run some tests here.

		# See if the output file already exists. if it doese, then we stop here
		if os.path.isfile(self._outputFile) :
			self._log_manager.log("INFO", "The " + self._outputFile + " exists so the process is being halted to prevent data loss.")
			return

		# Check to see if the captions file exists. If it doesn't we're all done for now
		if not os.path.isfile(self._sourceIllustrationsCaptions) :
			self._log_manager.log("ERRR", "The illustration caption file (" + self._sourceIllustrationsCaptions + ") is missing from the project. This process cannot work without it.")
			return

		# Check to see if the path to the illustrations lib is good. If it doesn't we're done
		if not os.path.isdir(self._sourceIllustrationsLibPath) :
			self._log_manager.log("ERRR", "The path to the illustrations library (" + self._sourceIllustrationsLibPath + ") does not seem to be correct. This process cannot work without it.")
			return

		# Check to see if the data file exists. If it doesn't we're done because we need that too
		if not os.path.isfile(self._sourceIllustrationsLibData) :
			self._log_manager.log("ERRR", "The illustration data file (" + self._sourceIllustrationsLibData + ") seems to be missing from the library. This process cannot work without it.")
			return

		# Assumption: If a custom encoding process exists, we process
		# the captions.csv file in the source folder and deposit the
		# results in the Illustrations folder in the project. If an
		# encoding process is not required, then we will just copy
		# the captions.csv file directly, trusting that it is ready
		# to be used.
		# However, it should be noted that at this time the encoding
		# conversion aspect of this has not been tested and probably
		# doesn't work at all because these encoding transformation
		# processes are complex, more work is needed in this area
#		chain = self._settings['Encoding']['Processing']['customEncodingProcess']
		chain = ""
		if chain != "" :
			mod = __import__("transformCSV")
			# We'll give the source, target, encoding chain and field to transform
			res = mod.doIt(self._projectIllustrationsCaptions, self._sourceIllustrationsCaptions, chain, 8)
			if res != None :
				self._log_manager.log("ERRR", res)
				return
			else :
				self._log_manager.log("INFO", "The " + self._sourceIllustrationsCaptions + " has been copied to the project Illustrations folder with an encoding tranformation on the caption field.")

		# If there is no encoding chain a simple file copy will do
		else :
			x = shutil.copy(self._sourceIllustrationsCaptions, self._projectIllustrationsCaptions)
			self._log_manager.log("INFO", "The " + self._sourceIllustrationsCaptions + " has been copied to the project Illustrations folder.")


		# If we didn't bail out right above, we'll go ahead and open the data file
		# The assumption here is that the encoding of the pieces of the csv are
		# what they need to be.
		inFileData = filter(lambda l: l[1]==self._bookID,
					csv.reader(open(self._projectIllustrationsCaptions), dialect=csv.excel))
		# Right here we will sort the list by BCV. This should prevent unsorted
		# data from getting out into the piclist.
		inFileData.sort(cmp=lambda x,y: cmp(x[1],y[1]) or cmp(int(x[2]),int(y[2])) or cmp(int(x[3]),int(y[3])))
		# Do not process unless we are in the right book and
		# keep track of the hits for this book
		hits = 0
		for line in inFileData :
			if self._bookID.upper() == line[1].upper() :
				hits +=1
				# If this next process fails, should we stop here? Hmmm...
				self.processIllustrationFile(line[0])

		# Now we need output anything we might have collected. If nothing was
		# found, just an empty file will be put out.
		if hits > 0 :
			self._outFileObject = codecs.open(self._outputFile, "w", encoding='utf_8_sig')
			self._log_manager.log("DBUG", "Created file: " + self._outputFile)
			self._outFileObject.writelines(self.collectPicLine(*line) + '\n' for line in inFileData)

			# Close the piclist file
			self._outFileObject.close()

		# Tell the world what we did
		self._log_manager.log("INFO", "We processed " + str(hits) + " illustration line(s) for: " + self._bookID)



# This starts the whole process going
def doIt(log_manager):
	thisModule = MakePiclistFile(log_manager)
	return thisModule.main()
