#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20080529
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This class will handle process log functions. Every process
# will report through the log manager class so good records
# are kept of all the processes performed on Scripture texts.

# History:
# 20080529 - djd - Initial draft
# 20081023 - djd - Refactor project.conf structure changes
# 20081028 - djd - Removed error handling from this class
# 20081030 - djd - Added handling of input and output file
#        information in the log object
# 20081119 - djd - Removed error count from output


#############################################################
#################### Initialize The Process #################
#############################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os, sys

# Import supporting local classes
import tools
from error_manager import *
from datetime import *

# Instantiate local classes
error_manager = ErrorManager()

class LogManager (object) :

	# Intitate the whole class
	def __init__(self) :

		# Pull in the system and project settings into one
		# object that will be passed along with this object.
		self._settings = tools.getSettingsObject()
		self._logFolder = ""
		self._logProcessID = ""
		self._processLogFile = ""
		self._processLogObject = []
		self._publicationType = ""
		self._currentProcess = ""
		self._currentSubProcess = ""
		self._currentTargetID = ""
		self._currentInput = ""
		self._currentOutput = ""
		self._currentVerse = ""
		self._currentChapter = ""
		self._currentBook = ""
		self._currentLocation = ""
		self._currentContext = ""
		self._errorCount = 0
		self._warningCount = 0
		self._optionalPassedVariable = ''


	def initializeLog (self, processToRun, targetID, inputFile, outputFile, optVar) :
		'''This will intialize the session logs. There are two logs that will be written to
			one is the system log and the other is the project log. Both are/will be located
			in the project Log folder.'''

		# Set up for this session
		self._logFolder = os.getcwd() + "/" + self._settings['System']['Paths'].get('PATH_LOG', 'Log')
		self._publicationType = self._settings['Format'].get('publicationType', 'scripture')
		self._currentProcess = processToRun
		self._currentTargetID = targetID
		self._currentInput = inputFile
		self._currentOutput = outputFile
		self._optionalPassedVariable = optVar

		# When are we doing this?
		date_time, secs = str(datetime.now()).split(".")

		# Who's doing this
		userName = tools.getSystemUser()

		# Don't bring in any errors or warnings
		self._errorCount = 0
		self._warningCount = 0

		# Event log initialization
		self._logProcessID = self._currentProcess + "-" + self._currentTargetID.lower()
		self._processLogFile = self._logFolder + "/" + self._logProcessID + ".log"
		# If the log file already exists we need to kill it now
		if os.path.isfile(self._processLogFile) :
			os.remove(self._processLogFile)

		self._currentProcess = processToRun
		self._processLogObject.append("File = " + self._currentInput + "\n")
		self._processLogObject.append("Book ID = " + self._currentTargetID + "\n")
		self._processLogObject.append("Process = " + processToRun.upper() + "\n")
		self._processLogObject.append("Publication Type = " + self._publicationType + "\n")
		self._processLogObject.append("User = " + userName + "\n")
		self._processLogObject.append("Date/Time = " + date_time + "\n")


	def resetLocation (self) :
		'''Manually reset all location component vars.'''

		self._currentVerse = ""
		self._currentChapter = ""
		self._currentBook = ""


	def setLocation (self, book, tag, num) :
		'''Set the location value with the proper formated string.'''

		# Trim off any extra stuff that might come in on the ID line
		# We really only need the first three chars fromthe ID line
		if len(book) > 3 :
			book = book[:4].strip().upper()

		# Set the book ID
		self._currentBook = book
		# Set the chapter number
		if tag == 'c' :
			self._currentChapter = num
		# Set the verse number
		elif tag == 'v' :
			self._currentVerse = num

		if self._currentBook :
			self._currentLocation = self._currentBook
			if self._currentChapter :
				self._currentLocation = self._currentBook + " " + self._currentChapter
			if self._currentVerse :
				self._currentLocation = self._currentBook + " " + self._currentChapter + ":" + self._currentVerse
		else :
			self._currentLocation = "BEGIN"


	def log (self, entryType, event, toTerm = 'false') :
		'''This will be a simple ini type output the value can be
			parsed as simple CVS. The output params are:
			entryType = ERRR, WARN, INFO
			context = A chunk of text which triggered the log event
			event = A brief description of the log event'''

		# Our version of a UID
		entryID = tools.makeUID()

		# Add sub process if there is one
		if self._currentSubProcess :
			event = self._currentSubProcess + ": " + event

		# for consistant quoting (I think)
		newEvent = event.replace('"', '""')
		context = self._currentContext.replace('"', '""')

		# Assemble the CSV entry line
		entry = '"' + entryID + '","' + entryType + '","' + context + '","' + \
				self._currentLocation + '","' + newEvent + '"'

		#Collect the entry
		self._processLogObject.append(entry + "\n")

		# If for some reason we fail to find a debugMode setting we will default
		# to debug output
		try :
			if self._settings != None and self._settings['System']['ErrorHandling']['Python']['debugMode'] == 'true' :
				tools.userMessage(entryType + ": " + event)
		except :
			tools.userMessage(entryType + ": " + event)

		# To save on code we will give the option to output this same message to
		# the termina which could be very handy in many cases
		if toTerm.lower() == 'true' :
			tools.userMessage(entryType + ": " + event)

		# Because there are so many ways to create errors we need just a simple
		# way to track them across seperate processes.  This will be done with a
		# simple error.log.  Each time an error is found it will be added to the
		# object.  The object will be written out at the end of the process.
		# The error.log file will continue to colect error repors until the
		# series of processes are done then the system will collect them all and
		# report.

		if entryType == "ERRR" or entryType == "WARN" :
			errorID = self._logProcessID + "." + entryID
			errorEntry = '"' + errorID + '","' + entryType + '","' + \
			self._currentLocation + '","' + context + '","' + newEvent + '"'
			error_manager.recordError(errorEntry)

		# Don't forget to count the errors
		if entryType == "ERRR" :
			self._errorCount +=1
		elif entryType == "WARN" :
			self._warningCount +=1


	def closeOutSessionLog (self) :
		'''This will write out all the logged entries to the log files at the
		end of a process.  However, we will first check to see if we are in a
		valid project area.  If not, it all comes to a crashing halt.'''

		if tools.isProjectFolder() == True :

			# First we need to be sure there is a Log folder to write to
			if os.path.isdir(self._logFolder) == False :
				os.mkdir(self._logFolder)

			# Close process log
			if os.path.isfile(self._processLogFile) == True :
				processWriteObject = codecs.open(self._processLogFile, "a", encoding='utf_8')
			else :
				processWriteObject = codecs.open(self._processLogFile, "w", encoding='utf_8')

			for line in self._processLogObject :
				processWriteObject.write(line)

			processWriteObject.close()
			self._processLogObject = []

		else:
			tools.userMessage("Sorry, cannot write out the log files because we do not seem to be inside a project.")

	flush = closeOutSessionLog
