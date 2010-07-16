#!/usr/bin/python2
# -*- coding: utf_8 -*-
# version: 20080423
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This script will create a simple backup file that will be
# put in the root of the project. This serves kind of like a
# one-step undo, no more than that.

# History:
# 20080917 - djd - Initial draft
# 20081004 - djd - Added some of the final touches to the
#		first cut of this feature.
# 20081023 - djd - Refactored due to changes in project.conf
# 20081028 - djd - Removed system logging, messages only now


#############################################################
######################### Load Modules ######################
#############################################################
# Firstly, import all the modules we need for this process

import tarfile

# Import supporting local classes
from tools import *
tools = Tools()

class BackupProject (object) :


	def main (self) :
		'''Here we will manage the backup process.'''

		self.settings = tools.getSettingsObject()
		# This is found in the project.conf file
		lastBackup = int(self.settings['System']['Backup']['lastBackup'])
		now = int(tools.makeDateStamp())

		# We'll do the backup now
		self.doBackup()

		# Update the backup time stamp in project.conf
		# Get the actual project.conf object
		projConf = tools.getProjectSettingsObject()
		# Update the setting you need to change
		projConf['System']['Backup']['lastBackup'] = now
		# Write out the setting to make it permenent
		projConf.write()
		# This updates the changes for this session
		self.settings['System']['Backup']['lastBackup'] = now


	def doBackup (self) :
		'''This is the main backup process.'''

		# For the location we use whatever the makefile.conf file has
		# whether it is abs or relative. Note, we use abs in archive_project.py
		backupFilePath = self.settings['System']['Backup']['backupPath']
		backupFile = backupFilePath + "/Backup.tar.gz"

		# Let's look to see if the Backup folder is there
		if not os.path.isdir(backupFilePath) :
			os.mkdir(backupFilePath)

		tar = tarfile.open(backupFile, 'w:gz')
		tar.add('.')
		tar.close()

		# Tell the world what we did
		tools.userMessage('INFO: Project has been backed up')


# This starts the whole process going
def doIt():

	thisModule = BackupProject()
	return thisModule.main()
