#!/usr/bin/python2
# -*- coding: utf_8 -*-
# version: 20100607
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This script facilitates the running of text processes on
# source and working text. Its job is to initialize the log
# file and close it out when everything is done.
#
#############################################################
#
# History:
# 20100607 - djd - Initial draft


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
#    UnicodeWarning: Unicode equal comparison failed to
#    convert both arguments to Unicode - interpreting them
#    as being unequal
# or
#    UnicodeDecodeError: 'ascii' codec can't decode byte
#    0xe2 in position 0: ordinal not in range(128)
#
# Regardless of which one you get or perhaps some others,
# everything grinds to a halt. The following code seems to
# work around the problem:

# Turns out this is a real hack and we have tried to implement
# a real solution by adding an encoding setting in the ConfigObj()
# calls we make. That is where it has actually been breaking.
# I will comment this for now and it can be taken out later
# after testing show that this approch works.
reload(sys)
sys.setdefaultencoding("utf-8")

# Import supporting local classes
import tools
from log_manager import *

# Instantiate local classes
tools        = Tools()
log_manager    = LogManager()

basePath = os.environ.get('PTXPLUS_BASE')
if not basePath :
	basePath = "/usr/share/xetex-ptxplus"
	os.environ['PTXPLUS_BASE'] = basePath

sys.path.append(basePath + '/bin/python')
sys.path.append(basePath + '/bin/python/lib_system')
sys.path.append(basePath + '/bin/python/lib_scripture')

# First position in the command line arg. is the task.
# We have to have that or the process fails
try :
	task            = sys.argv[1]
except :
	tools.userMessage("process_text.py: Cannot run the process because no module (task) has been specified.")
	sys.exit(1)

# Second position we add the file ID here so we can
# track what we are working on if we need to.
try :
	typeID            = sys.argv[2]
except :
	typeID            = "NA"

# In the third arg we have the input file name.
# There may be cases where this is not needed but
# this position always refers to the input file.
try :
	inputFile        = sys.argv[3]
except :
	inputFile        = ""

# Forth position we have the output file, just like the
try :
	outputFile = sys.argv[4]
except :
	outputFile        = ""

# We will use the fifth position to pass whatever else
# we might need to pass to the process.
try :
	optionalPassedVariable = sys.argv[5]
except :
	optionalPassedVariable    = ""


class RunProcess (object) :
	'''This will load the system process class we want to run.'''


	def main (self, task, typeID, inputFile, outputFile, optionalPassedVariable) :
		'''This is the main routine for the class. It will control
			the running of the process classes we want to run.'''

		# Set some global (might be better done in an init section)
		self._task = task
		self._typeID = typeID
		self._inputFile = inputFile
		self._outputFile = outputFile
		self._optionalPassedVariable = optionalPassedVariable


		# We need to sort out the task that we are running
		# Sometimes parent meta-tasks are being called which
		# need to link to the individual tasks. This sorts that
		# out and runs everthing that is called to run.

		# Make a list that contains all the metaProcesses
		metaTaskList = []
		taskList = []
		metaTaskList = log_manager._settings['System']['Processes']['textMetaProcesses']
		# if this is a meta task then we need to process it as
		# if there are multiple sub-tasks within even though
		# there may only be one
		if self._task in metaTaskList :
			metaTask = self._task
			taskList = log_manager._settings['System']['Processes'][metaTask]
			for thisTask in taskList :
				# It would be good if we gave a little feedback to the user
				# as to what exactly which processes are going to be run and
				# on what.
				head, tail = os.path.split(self._inputFile)
				tools.userMessage('INFO: Now running: ' + thisTask + ' (' + tail + ')')
				# The standard sys.argv[1] setting contains the name of the metaTask
				# However, that is not the name of the actual module we want to send
				# off to process. We need to replace sys.argv[1] with the right task
				# name and any parameters that go with it.
				sys.argv[1] = thisTask
				self.runIt(thisTask)

		# If it is not a meta task then it must be a single one
		# so we will just run it as it comes in
		else :
			self.runIt(self._task)


	def runIt (self, taskCommand) :
		'''This will dynamically run a module when given a
			valid name. The module must have the doIt() function
			defined in the "root" of the module.'''

		# For flexibility, some tasks may have parameters added
		# to them. To initiate the task we need to pull out the
		# the module name to be able to initialize it. Once the
		# module has been initialized, it will get the parmeters
		# from sys.argv[1] and take it from there.
		thisTask = taskCommand.split()[0]

		# Initialize the log manager to do its thing
		log_manager.initializeLog(thisTask, self._typeID, self._inputFile, self._outputFile, self._optionalPassedVariable)

		# For running each process we use one centralized task runner in tools.
		tools.taskRunner(log_manager, thisTask)

		# Close out the process by reporting to the log file
		log_manager.closeOutSessionLog()


#############################################################
################## Run the Process Class ####################
#############################################################


# Run the process called on
runClass = RunProcess()
runClass.main(task, typeID, inputFile, outputFile, optionalPassedVariable)
