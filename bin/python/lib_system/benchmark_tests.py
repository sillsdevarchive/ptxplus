#!/usr/bin/python2
# -*- coding: utf_8 -*-
# version: 20100707
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This module will run a series of checks on the working text
# using a copy of the working text that has been set aside
# as a benchmark. A diff viewer like Meld will be used to
# show the user what the differences are and they can decide
# what to do with it at that point.

# History:
# 20100910 - djd - Initial draft


#############################################################
######################### Load Modules ######################
#############################################################
# Firstly, import all the modules we need for this process

import sys, os, shutil

import tools

class BenchmarkTests (object) :


	def main (self, log_manager) :
		'''This is the main process function for benchmark testing.'''

		tools.userMessage('INFO: Begining benchmark testing')
		# Set the mode
		self._log_manager = log_manager

		# Gather up the initial settings
		basePath                = os.environ.get('PTXPLUS_BASE')
		pathHome                = os.path.abspath(tools.pubInfoObject['Paths']['PATH_HOME'])
		pathTexts         = pathHome + '/' + tools.pubInfoObject['Paths']['PATH_TEXTS']
		pathBenchmark             = pathHome + '/' + tools.pubInfoObject['Paths']['PATH_BENCHMARK']

# Need to add a broadcast var to the logging routine so we don't have to double up on comands

		# Do some sanity testing
		if not os.path.isdir(pathBenchmark) :
			tools.userMessage('WARN: No benchmark data was found, creating data set now. No checks will be run this time.')
			self._log_manager.log('WARN', 'No benchmark data was found, creating data set now. No checks will be run this time.')

#define makebenchmark
#@if test -r "$(PATH_BENCHMARK)"; then \
#	echo INFO: Benchmark exists: $(PATH_BENCHMARK); \
#	echo INFO: Will do comparisons here with diff and Meld; \
#else \
#	echo INFO: Creating benchmark files in $(PATH_BENCHMARK); \
#	mkdir -p $(PATH_BENCHMARK); \
#	cp $(PATH_TEXTS)/* $(PATH_BENCHMARK); \
#fi
#endef


			##############################################
			# Create the new benchmark data set here
			##############################################

			return

		else :
			# run whatever tests we can do here here

			# Open the diff viewer if needed, otherwise just report to the log

			return




# This starts the whole process going
def doIt(log_manager):

	thisModule = BenchmarkTests()
	return thisModule.main(log_manager)
