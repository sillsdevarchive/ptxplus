#!/usr/bin/python2
# -*- coding: utf_8 -*-
# version: 20080423
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This script will setup a new project for the user by asking
# questions for project parameters, then taking that data
# and pushing to the Makefile which runs the system. This
# will setup the project. After that it will produce a script
# just for that specific project which will allow the user
# run processes without having to input project parameters
# each time.

# History:
# 20080508 - djd - Initial draft
# 20080514 - djd - Added three-level project support
# 20080523 - djd - Moved location of default_settings ini files
#        Also changed to use script code for second
#        level description.
# 20080608 - djd - Added a help command system to remind the
#        user of what commands are availible, also
#        added a copy of defaul settings to make setup
#        easier.
# 20080611 - djd - Moved to Python folder. This will now be
#        called from the typeset script only.
# 20080627 - djd - Moved to the lib_system folder.
# 20080704 - djd - Moved make_tex_hyphenation_file and
#        make_process_instructions_file out to the
#        makefile system.
# 20080801 - djd - Added version stamping for the project.ini
#        files to prevent running processes on project
#        data without updating the project.ini file.
# 20081028 - djd - Removed system logging, messages only now
# 20081111 - djd - Changed to using the makeNecessaryFiles()
#        function to create a basic project. This is
#        much simpler and will help things stay more
#        consistant.

#############################################################
######################### Load Modules ######################
#############################################################
# Firstly, import all the modules we need for this process

import os, shutil, codecs, tarfile

# Import supporting local classes
import tools


#############################################################
#################### Main Module Defined ####################
#############################################################

class MakeNewProject (object) :


	def main (self, newFolderName, projType) :
		'''Create a new project at the specified path.'''

		# Just in case it isn't already a full path
		newProjectPath = os.path.abspath(newFolderName)

		tools.makeNecessaryFiles(newProjectPath, projType)

		# Tell the world what we did
		tools.userMessage('INFO: Created new project at: ' + newProjectPath)


# This starts the whole process going
def doIt(pathToProject, projType) :

	thisModule = MakeNewProject()
	return thisModule.main(pathToProject, projType)

