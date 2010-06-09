#!/usr/bin/python
# -*- coding: utf-8 -*-
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

# Import supporting local classes
from tools import *
from log_manager import *

# Instantiate local classes
tools		= Tools()
log_manager	= LogManager()

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
	task			= sys.argv[1]
except :
	tools.userMessage("process_text.py: Cannot run the process because no module (task) has been specified.")
	sys.exit(1)

# Second position we add the file ID here so we can
# track what we are working on if we need to.
try :
	typeID			= sys.argv[2]
except :
	typeID			= "NA"

# In the third arg we have the input file name.
# There may be cases where this is not needed but
# this position always refers to the input file.
try :
	inputFile		= sys.argv[3]
except :
	inputFile		= ""

# Forth position we have the output file, just like the
try :
	outputFile = sys.argv[4]
except :
	outputFile		= ""

# We will use the fifth position to pass whatever else
# we might need to pass to the process.
try :
	optionalPassedVariable = sys.argv[5]
except :
	optionalPassedVariable	= ""


class RunProcess (object) :
	'''This will load the system process class we want to run.'''


	def main (self, task, typeID, inputFile, outputFile, optionalPassedVariable) :
		'''This is the main routine for the class. It will control
			the running of the process classes we want to run.'''

		# We need to sort out the task that we are running
		# Sometimes parent meta-tasks are being called which
		# need to link to the individual tasks. This sorts that
		# out and runs everthing that is called to run.

		# Make a list that contains all the metaProcesses
		metaTaskList = []
		taskList = []
		import pdb; pdb.set_trace()
		metaTaskList = log_manager._settings['Process']['Processes']['metaProcesses']

		# if this is a meta task then we need to process it as
		# if there are multiple sub-tasks within even though
		# there may only be one
		if task in metaTaskList :
			metaTask = task
			taskList = log_manager._settings['Process']['Processes'][metaTask]
			for thisTask in taskList :
				self.runIt(thisTask)

		# If it is not a meta task then it must be a single one
		# so we will just run it as it comes in
		else :
			self.runIt(task)


	def runIt (self, thisTask) :
		'''This will dynamically run a module when given a
			valid name. The module must have the doIt() function
			defined in the "root" of the module.'''

		# Go a head and do it if we have not reached our error limit
		if log_manager.reachedErrorLimit() != True :

			# Initialize the log manager to do its thing
			log_manager.initializeLog(thisTask, typeID, inputFile, outputFile, optionalPassedVariable)

			# This will dynamically import the module
			# This will work because all the right paths have
			# been defined earlier.
			try :
				module = __import__(thisTask, globals(), locals(), [])
			except :
				tools.userMessage("Hmmm, cannot seem to import the \"" + thisTask + "\" module. This will not bode well for the rest of the process.")

			# Tell the log what we're doing.
			log_manager.log("DBUG", "Starting process: " + thisTask)

			# Run the module
			module.doIt(log_manager)
			log_manager.log("DBUG", "Process completed: " + thisTask)

			# Close out the process by reporting to the log file
			log_manager.closeOutSessionLog()
			warn = ""
			if log_manager._warningCount > 0 :
				warn = " (Warnings = " + str(log_manager._warningCount) + ")"
			tools.userMessage(thisTask + " completed " + typeID + " with " + str(log_manager._errorCount) + " errors" + warn)
		else :
			tools.userMessage("Did not run: [" + thisTask + "] Errors exceed limit.")





#############################################################
################## Run the Process Class ####################
#############################################################


# Run the process called on
runClass = RunProcess()
runClass.main(task, typeID, inputFile, outputFile, optionalPassedVariable)
