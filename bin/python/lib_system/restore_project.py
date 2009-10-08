#!/usr/bin/python
# -*- coding: utf-8 -*-
# version: 20080423
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This script will restore a backup of a project from the
# project_backup.tar.gz file found in the root of the project.

# History:
# 20080803 - djd - Initial draft
# 20081023 - djd - Refactor project.conf structure changes
# 20081028 - djd - Removed system logging, messages only now


#############################################################
######################### Load Modules ######################
#############################################################
# Firstly, import all the standard Python modules we need for
# this process

import tarfile

# Import supporting local classes
from tools import *
tools = Tools()

#############################################################
#################### Main Module Defined ####################
#############################################################

class RestoreProject (object) :


	def main (self) :
		'''This is the main function for restoring a project from a backup.
			We assume that we are starting from inside the project folder.'''

		settings = tools.getSettingsObject()
		# For the location we use whatever the makefile.conf file has
		# whether it is abs or relative. Note, we use abs in archive_project.py
		backupFilePath = settings['General']['Backup']['backupPath']
		backupFile = backupFilePath + "/Backup.tar.gz"

		tar = tarfile.open(backupFile, 'r:gz')
		tar.extractall()
		tar.close()

		# Tell the world what we did
		tools.userMessage("Restore project completed.")


# This starts the whole process going
def doIt() :

	thisModule = RestoreProject()
	return thisModule.main()
