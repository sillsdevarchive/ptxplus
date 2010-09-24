#!/usr/bin/python2
# -*- coding: utf_8 -*-
# version: 20100910
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

import sys, os, shutil, stat

import tools

class BenchmarkTests (object) :


	def main (self, log_manager) :
		'''This is the main process function for benchmark testing.'''

		# INITIAL SETTINGS
		self._log_manager = log_manager
		useBenchmarkTests       = self._log_manager._settings['System']['General']['useBenchmarkTests']
		visualDiffChecking      = self._log_manager._settings['System']['General']['visualDiffChecking']
		basePath                = os.environ.get('PTXPLUS_BASE')
		pathHome                = os.path.abspath(tools.pubInfoObject['Paths']['PATH_HOME'])
		pathBenchmark           = os.path.abspath(tools.pubInfoObject['Paths']['PATH_BENCHMARK'])
		new                     = self._log_manager._currentInput
		old                     = ''
		newFile                 = ''
		oldFile                 = ''
		switch                  = self._log_manager._optionalPassedVariable

		# SET TYPE (BUILD ADDITIONAL PATHS)
		# Set the test type (if we don't know, we don't go)
		if os.path.isfile(new) :
			testType = 'file'
			# Do some file name manipulation to get our old and new file names
			# It is assumed that we are working in the "Texts" folder and no
			# other. This might come back to bite us at some point.
			head, tail = os.path.split(new)
			old                     = pathBenchmark + '/' + head.split('/')[-1]
			newFile = new
			oldFile = old + '/' + tail
			self._log_manager.log('INFO', 'Benchmark type is file (' + os.path.split(new)[-1] + ')', 'true')
		elif os.path.isdir(new) :
			testType = 'dir'
			head, tail = os.path.split(new)
			old                     = pathBenchmark + '/' + tail
			self._log_manager.log('INFO', 'Benchmark type is folder (' + str(len(os.listdir(new))) + ' items)', 'true')
		else :
			self._log_manager.log('ERRR', 'Benchmark for [' + new + '] target type unknown', 'true')
			sys.exit(1)

		# MASTER SWITCH
		# Do not do anything if useBenchmarkTests is set to false
		if useBenchmarkTests.lower() == 'false' :
			self._log_manager.log('INFO', 'Benchmark tests have been turned off', 'true')
			return
		else :
			tools.userMessage('INFO: Starting benchmark tests')

		# UTILITY FUNCTIONS
		# There are some small tasks that can be done by this module
		# and are triggered by an optionally passed switch var.

		# Set the current component as the benchmark
		if switch.lower() == 'set' :
			# Deal with any exsiting file
			if os.path.isfile(oldFile) :
				os.unlink(oldFile)

			# Copy file and set permission to read-only
			shutil.copy(newFile, oldFile)
			os.chmod(oldFile, stat.S_IREAD)
			self._log_manager.log('INFO', 'Setting the current component as benchmark (' + os.path.split(new)[-1] + ')', 'true')

		# SANITY TESTING
		# If we survived to this point, do some sanity testing
		# First see if the benchmark folder is there then copy
		# whatever files are needed.
		if not os.path.isdir(old) :
			self._log_manager.log('INFO', 'No benchmark found, creating benchmark', 'true')
			os.makedirs(old)
			if testType == "file" :
				# Copy one file and set to readonly
				shutil.copy(newFile, oldFile)
				os.chmod(oldFile, stat.S_IREAD)
			elif testType == "dir" :
				# Copy all the files and set all of them to readonly
				tools.copyFiles(new, old)
				tools.chmodFiles(old, stat.S_IREAD)

		# Other tests for whole folder
		if os.path.isdir(new) :

			# If there are absolutely no files in the benchmark for
			# for some odd reason, copy them over from the new target
			# and make them all readonly
			if len(os.listdir(old)) == 0 :
				self._log_manager.log('INFO', 'No items in benchmark, copying from new target', 'true')
				if testType == "file" :
					# Copy one file and set to readonly
					os.unlink(oldFile)
					shutil.copy(newFile, oldFile)
					os.chmod(oldFile, stat.S_IREAD)
				elif testType == "dir" :
					# Copy all the files and set all of them to readonly
					tools.unlinkFiles(old)
					tools.copyFiles(new, old)
					tools.chmodFiles(old, stat.S_IREAD)

			# If the number of files is unequal, alert the user and
			# let them sort it out. It would be nice if this was more
			# automated but it is better to be manual at this point to
			# be safe.
			if len(os.listdir(new)) != len(os.listdir(old)) :
				self._log_manager.log('WARN', 'Benchmark out of sync with new target', 'true')
				self._log_manager.log('INFO', 'Target = ' + str(len(os.listdir(new))) + ' - Benchmark = ' +str(len(os.listdir(old))), 'true')

		# Other tests for individual component
		elif os.path.isfile(newFile) :
			if not os.path.isfile(oldFile) :
				self._log_manager.log('INFO', 'No benchmark file found, creating benchmark file', 'true')
				shutil.copy(newFile, oldFile)
				os.chmod(oldFile, stat.S_IREAD)


		# DIFF CHECK
		# Folder Diff test
		if testType.lower() == 'dir' :
			# Build the command
			sysCommand = "diff " + old + " " + new + " > /dev/null"
			self._log_manager.log('INFO', 'Doing initial folder DIFF check', 'true')
			# Send off the command return error code
			if os.system(sysCommand) != 0 :
				self.openMeld(old, new, visualDiffChecking)
			else :
				self._log_manager.log('INFO', 'No problems found, benchmark check complete', 'true')
		# File Diff test
		elif testType.lower() == 'file' :
			# Build the command
			sysCommand = "diff " + oldFile + " " + newFile + " > /dev/null"
			self._log_manager.log('INFO', 'Doing initial file DIFF check', 'true')
			# Send off the command return error code
			if os.system(sysCommand) != 0 :
				self.openMeld(oldFile, newFile, visualDiffChecking)
			else :
				self._log_manager.log('INFO', 'No problems found, benchmark check complete', 'true')


	def openMeld (self, oldFile, newFile, useViewer) :
		'''Open Meld to view the differences. NOTE: This may need to
			be mademore generalized in the future.'''

		# The user may not want to deal with the diff problems
		# that are showing up. As such, we will see if the viewer
		# has been turned off.
		if useViewer.lower() == 'true' :
			self._log_manager.log('INFO', 'Problems found. Now opening Meld', 'true')
			# Build the command (try terminating with the "&" for better control, I think.)
			sysCommand = "meld " + oldFile + " " + newFile + ' &'
			self._log_manager.log('INFO', 'Opening Meld diff viewer', 'true')
			# Send off the command return error code
			os.system(sysCommand)
		else :
			self._log_manager.log('ERRR', 'Benchmark failed. Turn on visual checking to see why.', 'true')



# This starts the whole process going
def doIt(log_manager):

	thisModule = BenchmarkTests()
	return thisModule.main(log_manager)
