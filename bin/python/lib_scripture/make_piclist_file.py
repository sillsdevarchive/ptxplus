#!/usr/bin/python2.5
# -*- coding: utf_8 -*-
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
#       there are no pictures to process. This solves
#       a dependency problem in makefile
# 20081023 - djd - Refactored due to changes in project.conf
# 20081030 - djd - Added total dependence on log_manager.
#       This script will not run without it because
#       it handles all the parameters it needs.
# 20081230 - djd - Changed over to work stand-alone instead
#       of through version control.
# 20090504 - djd - Added a filter for peripheral matter files
# 20091214 - djd - Added a check for missing lib info. If not
#       found then it is reported and the process is
#       halted.
# 20100414 - djd - Changed the way process works by adding a
#       lib data file and limiting the project file to
#       only containing caption and location info.
# 20100512 - djd - Changes to the caption copy process and
#       illustration handling. There is now linking
#       from a shared folder to the project.
# 20100616 - djd - Adjusted conf call due to conf file
#       reorg. Also removed tabs.


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
		self._texsize = self._settings['Format']['Illustrations'].get('size','col')
		self._texpos = self._settings['Format']['Illustrations'].get('position','tl')
		self._texscale = self._settings['Format']['Illustrations'].get('scale',1.0)
		self._chpVerSep = self._settings['Format']['Illustrations'].get('chpVerSep',':')
		self._captionRef = self._settings['Format']['Illustrations'].get('captionRef','true')
		self._captionProcessing = self._settings['Format']['Illustrations'].get('captionProcessing','')
		self._inputFile = log_manager._currentInput
		self._outputFile = self._inputFile + ".piclist"
		self._outFileObject = {}
		self._sourcePath = os.path.abspath(self._settings['System']['Paths']['PATH_SOURCE'])
		self._captionsFileName = self._settings['System']['Files']['FILE_ILLUSTRATION_CAPTIONS']
		self._sourceIllustrationsLibDataFileName = self._settings['System']['Files']['FILE_ILLUSTRATION_DATA']
		self._projectIllustrationsPath = os.path.abspath(self._settings['System']['Paths']['PATH_ILLUSTRATIONS'])
		self._sourceIllustrationsLibPath = os.path.abspath(self._settings['System']['Paths']['PATH_ILLUSTRATIONS_LIB'])
		self._sourceIllustrationsLibData = self._sourceIllustrationsLibPath + "/" + self._sourceIllustrationsLibDataFileName
		# The folder name for peripheral material is auto created here
		self._projectPeripheralFolderName = os.getcwd().split('/')[-1]
		self._projectPeripheralFolderPath = self._sourcePath + '/' + self._projectPeripheralFolderName
		self._projectIllustrationsCaptions = self._projectPeripheralFolderPath + "/" + self._captionsFileName
		self._libData = {}
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

		# Build the cv location ref (it must be in this format to work)
		loc = chapNum + "." + verseNum

		# Build the cv ref if it is wanted. Otherwise keep the ref string
		# empty so ptx2pdf leave it out
		if self._captionRef.lower() == 'true' :
			ref = chapNum + self._chpVerSep + verseNum
		else :
			ref = ''

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

		line = bookID.upper() + " " + loc + " |" + fileName + "|" + self._texsize + "|" + self._texpos + "|" + \
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

		# Build the file names, they should be all absolute paths
		source = self._sourceIllustrationsLibPath + "/" + fileName
		target = self._projectIllustrationsPath + "/" + fileName

		# Sanity test, we want to throw an error if the source
		# file isn't there
		if not os.path.isfile(source) :
			self._log_manager.log("ERRR", "The file: " + source + " was not found.")

		# Copy the picture file from the source to the target location
		# if it doesn't exist there already
		if os.path.isfile(target) :
			self._log_manager.log("DBUG", "The file: " + target + " already exists. This process will NOT overwrite it.")
		else :
			# copy and test (why is a successful return form shutil.copy "None" not helpful)
			x = shutil.copy(source, target)
			if os.path.isfile(target) :
				self._log_manager.log("DBUG", "Copied from: " + source + " ---To:--> " + target)
			else :
				self._log_manager.log("ERRR", "Failed to copy from: " + source + " ---To:--> " + target)


	def main(self):
		'''We will open up our captions file which should be Unicode
			encoded and in CSV format. The illustration IDs will
			be matched from that file with the lib data file and
			will create a piclist file for the book that is
			currently being processed.'''

		# Before we start we need to be sure our init succeeded so
		# we will run some tests here.

		# See if the output file already exists. if it does, then we stop here
		if os.path.isfile(self._outputFile) :
			self._log_manager.log("INFO", "The " + self._outputFile + " exists so the process is being halted to prevent data loss.")
			self._errors +=1

		# Check to see if the captions file exists in the share folder
		# if it doesn't we're all done for now
		if not os.path.isfile(self._projectIllustrationsCaptions) :
			self._log_manager.log("ERRR", "The illustration caption file (" + self._projectIllustrationsCaptions + ") is missing from the project. This process cannot work without it.")
			self._errors +=1

		# Check to see if the path to the illustrations lib is good.
		if not os.path.isdir(self._sourceIllustrationsLibPath) :
			self._log_manager.log("ERRR", "The path to the illustrations library (" + self._sourceIllustrationsLibPath + ") does not seem to be correct. This process cannot work without it.")
			self._errors +=1

		# Check to see if the data file exists. If it doesn't we're done because we need that too
		if not os.path.isfile(self._sourceIllustrationsLibData) :
			self._log_manager.log("ERRR", "The illustration data file (" + self._sourceIllustrationsLibDataFileName + ") seems to be missing from the library. This process cannot work without it.")
			self._errors +=1

		# If we get an error we really can't go on at this point
		if self._errors != 0 :
			return

		# Pull in the library data file using the CSVtoDict class in tools
		try :
			self._libData = CSVtoDict(self._sourceIllustrationsLibData)
		except :
			self._log_manager.log("ERRR", "Not able to find (" + self._sourceIllustrationsLibData + "). More than likely the file is missing or the path is wrong.")

		# If we didn't bail out right above, we'll go ahead and open the data file
		# The assumption here is that the encoding of the pieces of the csv are
		# what they need to be.

		# Filter out any IDs that do not have anything to do with this book
		inFileData = filter(lambda l: l[1].lower() == self._bookID.lower(),
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
			self._outFileObject = codecs.open(self._outputFile, "w", encoding='utf_8')
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
