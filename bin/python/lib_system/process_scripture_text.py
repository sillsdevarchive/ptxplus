#!/usr/bin/python2.5
# -*- coding: utf-8 -*-
# version: 20080423
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This script facilitates the running of processes on the
# working version of the source text. This is a generic script
# which passes process information on to the scripts/modules
# that do the real work.
#
# Every process in the system will need to be defined in this
# script. It would be nice if there could be another way to
# drive this externally but for now this will do. The real
# advantage to this current setup is that everything goes
# through this one script. Should be easier for maintenance.
#
# Dependencies:
# Processing scripts are dependent on checking scripts. In
# the checking phase checks are run against the original text.
# Errors are then reported to the client who is responcible for
# correcting them. Any time a change is made to the source text
# the process checks will be rerun automatically.
#
# With these checks done and any errors found and corrected
# we can be sure that any necessary processes can be preformed
# without error. Up until this point the files are still in the
# "source" pool and have not been copied into the main system
# source file. When the checks are complete the copy script can
# copy the files and processes can be done.
#
#############################################################
#
# History:
# 20080528 - djd - Initial draft
# 20080601 - djd - Moved everything to be called from classes
# 20080619 - djd - Modified for new quote checking system.
# 20080623 - djd - Changed to accomodate a three phase
#		text processing system
# 20080624 - djd - Added dynamic module loading
# 20080812 - djd - Added basePath setting for better module
#		loading as this script runs under makefile.
# 20080819 - djd - Added custom process running.
# 20080825 - djd - Removed custom process running
# 20081020 - djd - Change error limit checking on copy from
#		source so that 0 = infinite.
# 20081023 - djd - Refactor project.conf structure changes
# 20081028 - djd - Added error handling


#############################################################
#################### Initialize The Process #################
#############################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, sys

# Next is a work around for an internal encoding problem. At
# some point the python scripts get confused and start seeing
# the world as ASCI. This messes everything up and give an
# error like:
#	UnicodeWarning: Unicode equal comparison failed to
#	convert both arguments to Unicode - interpreting them
#	as being unequal
# or
#	UnicodeDecodeError: 'ascii' codec can't decode byte
#	0xe2 in position 0: ordinal not in range(128)
#
# Regardless of which one you get or perhaps some others,
# everything grinds to a halt. The following code seems to
# work around the problem:

reload(sys)
sys.setdefaultencoding("utf-8")

# This might be because this script is normally called by the
# makefile system so perhaps Python forgets it is supposed to
# be running in UTF-8 mode.

# Include some paths for our system
basePath = os.environ.get('PTXPLUS_BASE')
if not basePath :
	basePath = "/usr/share/xetex-ptxplus"
	os.environ['PTXPLUS_BASE'] = basePath

sys.path.append(basePath + '/bin/python')
sys.path.append(basePath + '/bin/python/lib_system')
sys.path.append(basePath + '/bin/python/lib_scripture')

# Import supporting local classes
from tools import *
from log_manager import *

# Instantiate local classes
tools		= Tools()
log_manager	= LogManager()

# Set some vars from the command arguments
task		= sys.argv[1]
bookID		= sys.argv[2].upper()
inputFile	= os.getcwd() + "/" + sys.argv[3]
# We may not get a 4th argument so we have to be careful
try :
	outputFile = os.getcwd() + "/" + sys.argv[4]

except :
	outputFile = "none"

# Set some other vars here
settings_project = tools.getProjectSettingsObject()



class RunProcesses (object) :
	'''This will dynamically load and run the modules we need
		one at a time as defined in the project.ini file.'''

	# Intitate the child classes.
	def __init__(self, log_manager, task, bookID, inputFile, outputFile) :

		self._settings = log_manager._settings
		self._task = task
		self._inputFile = inputFile
		self._outputFile = outputFile
		self._bookID = bookID


	def main (self) :
		'''This is the main routine for the class. It will control
			the running of the three types of text processes
			on the system. '''

		if self._task == "PreprocessChecks" :
			# Grab all the PreprocessChecks from settings_project
			for key, value in self._settings['General']['PreprocessChecks'].iteritems() :
				# Run any that are set to "true"
				# It shouldn't have any problems finding them as the
				# the path should include the right locations
				if value == "true" :
					self.runIt(key)

		elif self._task == "CopyIntoSystem" :
			# If everything is ok at this point we'll copy from source
			if self._settings['General']['CopyIntoSystem']['copy_from_source'] == "true" :
				self.runIt("copy_from_source")

		elif self._task == "TextProcesses" :
			# Grab all the text processes from settings_project
			for key, value in self._settings['General']['TextProcesses'].iteritems() :
				# Run any that are set to "true"
				if value == "true" :
					self.runIt(key)

		else :
			# Hmmm, it's hard to know if this is a valid process or not
			# We'll just trust that it is and try to run the task. If it
			# doesn't work then we'll see a problem in the output in the
			# terminal but ideally that's not a good way to work. Some
			# error feed-back would be desirable.
			self.runIt(task)


	def runIt (self, moduleName) :
		'''This will dynamically run a module when given a
			valid name. The module must have the doIt() function
			defined in the "root" of the module.'''

		# Go a head and do it if we have not reached our error limit
		if log_manager.reachedErrorLimit() != True :

			# Initialize the log manager to do its thing
			log_manager.initializeLog(moduleName, bookID, self._inputFile, self._outputFile)

			# This will dynamically import the module
			# This will work because all the right paths have
			# been defined earlier.
			module = __import__(moduleName, globals(), locals(), [])

			# Tell the log what we're doing.
			log_manager.log("DBUG", "Starting process: " + moduleName)

			# Run the module
			module.doIt(log_manager)
			log_manager.log("DBUG", "Process completed: " + moduleName)

			# Close out the process by reporting to the log file
			log_manager.closeOutSessionLog()
			warn = ""
			if log_manager._warningCount > 0 :
				warn = " (Warnings = " + str(log_manager._warningCount) + ")"
			tools.userMessage(moduleName + " completed " + self._bookID + " with " + str(log_manager._errorCount) + " errors" + warn)
		else :
			tools.userMessage("Did not run: [" + moduleName + "] Errors exceed limit.")




#############################################################
################## Run the Process Class ####################
#############################################################



# Run the process called on
runClass = RunProcesses(log_manager, task, bookID, inputFile, outputFile)
runClass.main()
