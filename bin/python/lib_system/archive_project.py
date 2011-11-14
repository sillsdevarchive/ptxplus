#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20080423
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# Archive a project in the system. There will be only one
# archive at a time so this module will replace any existing
# archive files with the same name. The archive file will
# include the source files and most of the project files.
# Log files and backup files will be removed before the
# archive .tar.gz file is made.

# History:
# 20080811 - djd - Initial draft
# 20080823 - djd - Removed archive of external source folder
# 20080828 - djd - Added file exclusion routine to leave
#		out any files we don't need in the archive
# 20081013 - djd - Worked out a way to use both the ptxplus
#		and the ptxplus-manager for intiating this
# 		process.
# 20081023 - djd - Refactored due to changes in project.conf
# 20081028 - djd - Removed system logging, messages only now


#############################################################
######################### Load Modules ######################
#############################################################
# Firstly, import all the modules we need for this process

import tarfile

# Import supporting local classes
import tools

class ArchiveProject (object) :


	def main (self, filename) :
		'''This is the process function for generating a project archive.
			We assume that we are starting in the project folder.'''

		# Get the project ID and path
		projectID = tools.getProjectID()
		projectPath = os.getcwd()
		self.settings = tools.getSettingsObject()
		print "File: " + filename
		# Output an archive.conf file that contains all the current settings
		# Though this is just a one-time operation it is easier to do it in tools
		archiveConfObject = tools.getProjectSettingsObject()
		if archiveConfObject != None :
			archiveConfObject['Process']['General']['LOCKED'] = 1
			archiveConfObject.filename = 'archive.conf'
			archiveConfObject.write()

		# Move into the parent folder to start the process (We want to
		# get the source files as well as the project files
		projHome, proj = os.path.split(projectPath)
		os.chdir(projHome)
		# Build a path to the archive folder default is ../../Archive
		# If it is not the default we'll assume the path is absolute
		if filename == projectID :
			archivePath = self.settings['General']['Archive']['archivePath']
			if archivePath.find('../..') > -1 :
				archivePath = os.getcwd() + '/Archive'
			archiveFile = archivePath + "/" + projectID + ".tar.gz"
			# Look and see if the Archive folder exists
			if not os.path.isdir(archivePath) :
				os.mkdir(archivePath)
		else :
			archiveFile = filename

		# Look to see if the archiveFile exists, if so, we'll delete it
		if os.path.isfile(archiveFile) :
			os.remove(archiveFile)

		# Now we'll move back into the project folder.
		os.chdir(projectPath)

		# Make the file list we want to tar.
		fileList = []
		for root, dirs, files in tools.walk('.') :

#			print root, dirs
			# Filter out all the files we don't want and
			# include a few we want to keep.
			for name in files :
				self.pruneDirs(root, dirs)
				if self.excludeFileFilter(name) != True and \
					self.excludeFileTypeFilter(name) != True or \
					self.includeFileFilter(name) == True :
					fileList.append(os.path.join(root, name))

			if root == '.' :
				self.pruneDirs(root, dirs)


		# Now make the archive file. However, we want to keep it from adding
		# any backup files and the .svn folders. This should make for eaiser
		# transfer between systems.
		tar = tarfile.open(archiveFile, 'w:gz')
		for file in fileList :
			tar.add(file)

		tar.close()

		# Tell the world what we did
		tools.userMessage('Archived project: ' + projectID)


	def includeFileFilter (self, name) :
		'''This is a filter function to identify files we want to
			inlude in the archive. Return True if we find one
			we want in the archive (want to inlude).'''

		try :
			includeFiles = self.settings['General']['Archive']['includeArchiveFiles'].split()
			for file in includeFiles :
				if name == file :
					return True
		except :
			return False


	def excludeFileFilter (self, name) :
		'''This is a filter function to identify files we want to
			exlude from the archive. Return True if we find one
			we don't want in the archive (want to exlude).'''

		try :
			excludeFiles = self.settings['General']['Archive']['excludeArchiveFiles'].split()
			for file in excludeFiles :
				if name == file :
					return True
		except :
			return False


	def excludeFileTypeFilter (self, name) :
		'''This is a filter function to identify types of files we
			want to exlude from the archive. Return True if we
			find a type of tile we don't want in the archive.
			True = we want to exclude this kind of file.'''

		# There are a couple types of files we know we don't want
		# such as backup files and hidden files.
		if name[-1:] == "~" or name[0:1] == "." :
			return True

		# If that didn't fire then we'll search the list
		else :
			try :
				excludeFileTypes = self.settings['General']['Archive']['excludeArchiveFileTypes'].split()
				for type in excludeFileTypes :
					if name.find(type) > -1 :
						return True
			except :
				return False


	def pruneDirs (self, root, dirs) :
		''' Remove all unwanted directories from the dirs list in place.'''

		try :
			excludeDirs = self.settings['General']['Archive']['excludeArchiveDirs'].split()
			c = 0
			while c < len(dirs) :
				if dirs[c] in (excludeDirs) :
					del dirs[c]
				else :
					c = c + 1
		except :
			tools.userMessage('No excludeArchiveDirs list found in project.conf')



# This starts the whole process going
def doIt(filename):

	thisModule = ArchiveProject()
	return thisModule.main(filename)
