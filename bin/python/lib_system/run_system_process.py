#!/usr/bin/python
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
# Dependencies:
# Processing scripts are dependent on checking scripts. In
# the checking phase checks are run against the original text.
# Errors are then reported to the client who is responsible for
# correcting them. Any time a change is made to the source text
# the process checks will be rerun automatically.
#
# With preprocess checks done and any errors found and corrected,
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
# 20081028 - djd - Removed system logging, messages only now


#############################################################
#################### Initialize The Process #################
#############################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, sys

basePath = os.environ.get('PTXPLUS_BASE')
if not basePath :
	basePath = "/usr/share/xetex-ptxplus"
	os.environ['PTXPLUS_BASE'] = basePath

sys.path.append(basePath + '/bin/python')
sys.path.append(basePath + '/bin/python/lib_system')
sys.path.append(basePath + '/bin/python/lib_scripture')

# All we should need to get things going is the projectID
task		= sys.argv[1]


class RunProcess (object) :
	'''This will load the system process class we want to run.'''


	def main (self, task) :
		'''This is the main routine for the class. It will control
			the running of the process classes we want to run.'''

		# This will dynamically import the module
		# This will work because all the right paths have
		# been defined earlier.
		module = __import__(task, globals(), locals(), [])

		# Run the module
		module.doIt()



#############################################################
################## Run the Process Class ####################
#############################################################


# Run the process called on
runClass = RunProcess()
runClass.main(task)
