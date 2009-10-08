#!/usr/bin/python
# -*- coding: utf-8 -*-
# version: 20080803
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This script will import a new project from an existing
# archive.

# History:
# 20080803 - djd - Initial draft
# 20081013 - djd - Changed behavior so whatever the base file
#		name is, this is what the project directory
#		will be called.
# 20081017 - djd - Changed behavior so it is more like a new
#		project creation. It will now put it in
#		whatever folder it is in at the time if there
#		are no other projects present.
# 20081028 - djd - Removed system logging, messages only now
# 20081111 - djd - Removed any auto folder creation code
#		because now it is automatically done when
#		the project is run the first time.


#############################################################
######################### Load Modules ######################
#############################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, tarfile, shutil

# Import supporting local classes
from tools import *

tools = Tools()

#############################################################
#################### Main Module Defined ####################
#############################################################

class ImportProject (object) :


	def main (self, archiveFile) :

		# Look to see if the archiveFile exists, if not, we stop here
		if os.path.isfile(archiveFile) == False :
			tools.userMessage('The archive: ' + archiveFile + ' does not exist. Sorry can\'t import the project')

		else :
			tar = tarfile.open(archiveFile, 'r:gz')

			# if directory already exists, bail out
			if tools.isProjectFolder() == True :
				tools.userMessage('There is already a project in this folder. Aborting import')
				return

			# Extract the tar file
			tar.extractall()
			tar.close()

			# Create the project.conf file from the archive.conf file
			shutil.move("archive.conf", "project.conf")

			# There may be additional folders and fles to add to make the
			# project complete. This depends on what version of ptxplus
			# was used to create the project. The project will be automatically
			# updated the first time it is run.

			# Tell the world what we did
			tools.userMessage('Import project complete')


# This starts the whole process going
def doIt(archiveFile) :

	thisModule = ImportProject()
	return thisModule.main(archiveFile)
