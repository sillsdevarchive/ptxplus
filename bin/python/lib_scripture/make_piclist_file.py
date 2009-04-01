#!/usr/bin/python
# -*- coding: utf-8 -*-
# version: 20080622
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This class will check the basic form of a given file.

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


#############################################################
#################### Initialize The Process #################
#############################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, sys, codecs, csv, shutil

# Import supporting local classes
from tools import *
tools = Tools()

class MakePiclistFile (object) :

	# Intitate the whole class
	def __init__(self, log_manager) :

		self._settings = log_manager._settings
		self._log_manager = log_manager
		self._inputFile = log_manager._currentInput
		self._bookID = log_manager._currentTargetID
		self._outputFile = self._inputFile + ".piclist"
		self._outFileObject = {}
		self._processIllustrationsPath = os.getcwd() + "/" + self._settings['Process']['Paths']['PATH_ILLUSTRATIONS']
		self._sourceIllustrationsLib = self._settings['General']['Resources']['Illustrations']['pathToIllustrationsLib'] + "/" + self._settings['General']['Resources']['Illustrations']['illustrationsLib']
		self._csvMasterFile = self._processIllustrationsPath + "/" + self._settings['General']['Resources']['Illustrations']['illustrationsControlFile']
		self._errors = 0


	def writePicLine (self, use, bid, cn, vn, fid, cr, cp) :
		'''Write out the illustration description line. The incoming
			file will not have all the information we need so we'll make
			some things up here and use them as defaults. The format goes
			like this:
				bid c.v |fileName|span|b/t|Copyright|Caption|
			Note the space after the v, that needs to be there or TeX
			will choke. Also, I think something needs to go after the
			caption field but I don't know what yet. Will add later.'''

		# Assuming png we'll add that here
		fileName = fid + ".png"
		# Is this an illustration that we'll be using?
		switch = ""
		if use.upper() != "TRUE" :
			switch = "%"

		line = switch + bid + " " + cn + "." + vn + " |" + fileName + "|span|b|" + cr + "|" + cp + "|"
		self._outFileObject.write(line + "\n")
		self._log_manager.log("DBUG", "Wrote out to piclist file: " + line)



	def processIllustration (self, fileID) :
		'''This is just a generalized illustration processing function.
			More will need to be done as this matures. The first assumption
			is that all the pictures we work with are in PNG format'''

		# Copy the picture file from the source to the target location
		source = self._sourceIllustrationsLib + "/" + fileID + ".png"
		target = self._processIllustrationsPath + "/" + fileID + ".png"

		if not os.path.isfile(target) :
			shutil.copy(source, target)
			self._log_manager.log("DBUG", "Copied from: " + source + " ---To:--> " + target)


	def main(self):
		'''We will open up our master piclist file which should be Unicode
			encoded and in CSV format. If that file doesn't exsist
			then we need to gracefully stop at that point. This will
			prevent other processes from crashing. We will go through
			the master piclist file and look for book IDs that match
			the current book we are working with. It will then create
			a piclist file for that book file so pdf2ptx can work with
			it. We will do this one book at a time.'''

# This needs to be rewritten to use the sfm parser so it will run more efficiently

		if not os.path.isfile(self._csvMasterFile) :
			# If it doesn't exist that isn't necessarily a problem
			# We'll just output a warning to the log and exit gracefully.

			self._log_manager.log("WARN", self._csvMasterFile + " does not exsist for this book ID.")
			return

		else :
			csvObject = csv.reader(open(self._csvMasterFile, "rb"))

		# The main dependency of this process is the master file. If
		# a change is made there we will have to rewrite the book.piclist
		# file. At least that's the way we're approching it right now.

		# Also, book files have a dependency on the .piclist files. This
		# being the case, we need to create one even if it is empty. Then,
		# when there are no changes the book will not be remade. We will
		# just open the file now and if there is anything that goes in it
		# that will fine. If not, that's okay too.

		self._outFileObject = codecs.open(self._outputFile, "w", encoding='utf-8')
		self._log_manager.log("DBUG", "Created file: " + self._outputFile)


		pics = 0

		for line in csvObject :

			# Throw out the header line (there should be one!)
			if pics == 0 :
				pics +=1
				continue
			else :
				if self._bookID == line[0] :
					# Now we'll write out what we've found
					# More error correction needs to go here
					# I would think but this will be ok to
					# start with.
					self.writePicLine(line[0].upper(), line[1].upper(), line[2], line[3], \
					line[5], \
					line[6], line[7])
					self.processIllustration(line[4])
					pics +=1


		# Close the piclist file
		self._outFileObject.close()

		# Tell the world what we did
		self._log_manager.log("INFO", "We processed " + str(pics-1) + " illustration line(s) for: " + self._bookID)



# This starts the whole process going
def doIt(log_manager):

	thisModule = MakePiclistFile(log_manager)
	return thisModule.main()
