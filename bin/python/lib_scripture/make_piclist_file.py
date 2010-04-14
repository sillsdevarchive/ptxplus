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

import os, sys, codecs, csv, shutil
from operator import itemgetter

# Import supporting local classes
from tools import *
tools = Tools()

class MakePiclistFile (object) :

	# Intitate the whole class and do some checks to see if we can continue or not
	def __init__(self, log_manager) :

		self._settings = log_manager._settings
		self._log_manager = log_manager
		self._log_manager._currentSubProcess = 'MakePiclistFile'
		self._bookID = log_manager._currentTargetID

		# If the file belongs to the peripheral mater we will not go through with the process
		self._inputFile = log_manager._currentInput
		if tools.isPeripheralMatter(self._inputFile) :
			self._log_manager.log("INFO", "The " + self._inputFile + " is part of the peripheral mater so the process is being halted.")
			return

		self._outputFile = self._inputFile + ".piclist"
		# See if the output file already exists. if it doese, then we stop here
		if os.path.isfile(self._outputFile) :
			self._log_manager.log("INFO", "The " + self._outputFile + " exists so the process is being halted to prevent data loss.")
			return

		self._outFileObject = {}
		self._processIllustrationsPath = os.getcwd() + "/" + self._settings['Process']['Paths']['PATH_ILLUSTRATIONS']
		self._sourcePath = self._settings['Process']['Paths']['PATH_SOURCE']

		self._sourceIllustrationsCaptions = self._sourcePath + "/captions.csv"
		# Check to see if the captions file exists. If it doesn't we're all done for now
		if not os.path.isfile(self._sourceIllustrationsCaptions) :
			self._log_manager.log("ERROR", "The illustration caption file (" + self._sourceIllustrationsCaptions + ") is missing from the project. This process cannot work without it.")
			return

		self._sourceIllustrationsLibPath = self._settings['Process']['Paths']['PATH_ILLUSTRATIONS_LIB']
		# Check to see if the captions file exists. If it doesn't we're all done for now
		if not os.path.isdir(self._sourceIllustrationsLibPath) :
			self._log_manager.log("ERROR", "The illustration library (" + self._sourceIllustrationsLibPath + ") is not where the project config file says it is. This process cannot work without it.")
			return

		(head, tail) = os.path.split(self._sourceIllustrationsLibPath)
		self._sourceIllustrationsLibData = self._sourceIllustrationsLibPath + "/" + tail + "_data.csv"
		# Check to see if the data file exists. If it doesn't we're all done for now
		if not os.path.isfile(self._sourceIllustrationsLibData) :
			self._log_manager.log("ERROR", "The illustration data file (" + self._sourceIllustrationsLibData + ") is missing from the library. This process cannot work without it.")
			return

		# Next pull in some default sizing params if they exist, if not use the default settings.
		self._texsize = self._settings['General']['Resources']['Illustrations'].get('size','col')
		self._texpos = self._settings['General']['Resources']['Illustrations'].get('position','tl')
		self._texscale = self._settings['General']['Resources']['Illustrations'].get('scale',1.0)

		self._errors = 0


	def collectPicLine (self, use, bid, cn, vn, fid, ils, cr, cp, tr, altr) :
		'''Collect and format an illustration description line. The incoming
			file will not have all the information we need so we'll make
			some things up here and use them as defaults. The format goes
			like this:
				bid c.v |fileName|span|b/t|Copyright|Caption|

			Note the space after the v, that needs to be there or TeX
			will choke. The caption field "cp" contains the English
			version of the caption. Next to that goes the translation
			field "tr" which holds the vernacular version of the
			caption field.

			The use field allows us to regulate the use of the whole
			row (record). That gets translated to the switch field.'''

		# Assuming png we'll add that here
		fileName = fid + ".png"
		# Is this an illustration that we'll be using?
		switch = ""
		if use.upper() != "TRUE" :
			switch = "%"

		caption = cp
		if tr != "" :
			caption = tr

		line = switch + bid + " " + cn + "." + vn + " |" + fileName + "|" + self._texsize + "|" + self._texpos + "|" + str(self._texscale) + "|" + cr + "|" + caption + "|"
		self._log_manager.log("DBUG", "Collected: " + line)
		return line

	def processIllustration (self, fileID) :
		'''This is just a generalized illustration processing function.
			More will need to be done as this matures. The first assumption
			is that all the pictures we work with are in PNG format'''

		# Build the file names
		source = self._sourceIllustrationsLib + "/" + fileID + ".png"
		target = self._processIllustrationsPath + "/" + fileID + ".png"
		# Check to see if the file is there or not. We don't want to copy
		# one in if one exists already.
		if not os.path.isfile(target) :
			# Copy the picture file from the source to the target location
			shutil.copy(source, target)
			self._log_manager.log("DBUG", "Copied from: " + source + " ---To:--> " + target)


	def main(self):
		'''We will open up our captions file which should be Unicode
			encoded and in CSV format. The illustration IDs will
			be matched from that file with the lib data file and
			will create a piclist file for the book that is
			currently being processed.'''

		# Assumption: If a custom encoding process exists, we process
		# However, it should be noted that at this time this has not
		# been tested and probably doesn't work at all because these
		# encoding transformation processes are complex, more work is
		# needed in this area
		chain = self._settings['Encoding']['Processing']['customEncodingProcess']
		if chain != "" :
			mod = __import__("transformCSV")
			# We'll give the source, target, encoding chain and field to transform
			res = mod.doIt(self._csvSourceFile, self._sourceIllustrationsCaptions, chain, 8)
			if res != None :
				self._log_manager.log("ERRR", res)
				return
			else :
				self._log_manager.log("INFO", "The " + self._sourceIllustrationsCaptions + " has been copied from the Source folder with an encoding tranformation on the caption field.")

		# If there is no encoding chain a simple file copy will do
		else :
			x = shutil.copy(self._csvSourceFile, self._sourceIllustrationsCaptions)
			self._log_manager.log("INFO", "The " + self._sourceIllustrationsCaptions + " has been copied from the Source folder.")


		# If we didn't bail out right above, we'll go ahead and open the data file
		# The assumption here is that the encoding of the pieces of the csv are
		# what they need to be.
		inFileData = filter(lambda l: l[1]==self._bookID,
					csv.reader(open(self._sourceIllustrationsCaptions), dialect=csv.excel))
		# Right here we will sort the list by BCV. This should prevent unsorted
		# data from getting out into the piclist.
		inFileData.sort(cmp=lambda x,y: cmp(x[1],y[1]) or cmp(int(x[2]),int(y[2])) or cmp(int(x[3]),int(y[3])))
		# Do not process unless we are in the right book and the
		# illustration is tagged to be used (True or False)
		for line in inFileData :
			self.processIllustration(line[4])

		# Now we need output anything we might have collected. If nothing was
		# found, just an empty file will be put out.
		self._outFileObject = codecs.open(self._outputFile, "w", encoding='utf_8_sig')
		self._log_manager.log("DBUG", "Created file: " + self._outputFile)
		self._outFileObject.writelines(self.collectPicLine(*line) + '\n' for line in inFileData)

		# Close the piclist file
		self._outFileObject.close()

		# Tell the world what we did
		self._log_manager.log("INFO", "We processed " + str(len(inFileData)) + " illustration line(s) for: " + self._bookID)



# This starts the whole process going
def doIt(log_manager):
	thisModule = MakePiclistFile(log_manager)
	return thisModule.main()
