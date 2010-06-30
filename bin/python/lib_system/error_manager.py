#!/usr/bin/python2.5
# -*- coding: utf_8 -*-
# version: 20081028
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This class will handle errors which are captured by the
# system. It should deal only with error situations.

# History:
# 20081028 - djd - Initial draft


#############################################################
#################### Initialize The Process #################
#############################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os, re

# Import supporting local classes
from tools import *
tools = Tools()

class ErrorManager (object) :

	# Intitate the whole class
	def __init__(self) :

		# We will just use the settings locally
		self._settings = tools.getSettingsObject()
		try :
			self._logFolder = os.getcwd() + "/" + self._settings['Process']['Paths']['PATH_LOG']

		except :
			self._logFolder = os.getcwd() + "/Log"

		self._errorLogFile = self._logFolder +  "/error.log"
		self._errorLogObject = []
		self._errorCount = 0


	def raiseErrorCount (self) :
		'''Just a simple error counting routine.'''

		self._errorCount += 1


	def getErrorCount (self) :
		'''Return the error count in this session.'''

		return self._errorCount



	def getErrorCountFromLog (self) :
		'''Just tell me how many errors there are in the log right now.'''

		count = 0
		if os.path.isfile(self._errorLogFile) :
			fileObject = codecs.open(self._errorLogFile, "r", encoding='utf_8')
			for line in fileObject :
				if line.find("ERRR") > 0 :
					count +=1

			return count
		else :
			print "No file found: " + self._errorLogFile
			return 0


	def outputProcessErrorReport (self) :
		'''Take a look at the error log and tell how many warnings and errors found.'''

		errrOutput = ""
		warnOutput = ""
		errrCount = 0
		warnCount = 0

		if os.path.isfile(self._errorLogFile) == True :
			try :
				fileObject = codecs.open(self._errorLogFile, "r", encoding='utf_8')
				errrOutput = "\nErrors found: \n"
				warnOutput = "\nWarnings found: \n"
				for line in fileObject :
					if line.find("ERRR") > 0 :
						errrCount +=1
					elif line.find("WARN") > 0 :
						warnCount +=1

				if errrCount > 0 :
					tools.userMessage("A total of " + str(errrCount) + " errors were found.")
					# Now we will add a more "in your face" error report so they are not ignored
					# It might be good to exchange the sed command for stanard Python regex code
					try :
						sed_filter = """sed -r 's/[[:blank:]]*("[^"]*")[[:blank:]]*,/\\1\\n/g' < Log/{log!r}"""\
								   """| sed -r 's/(^[[:blank:]]*"|"[[:blank:]]*$)//g'""".format
						dialog_command = "zenity --title={title!r} "\
												"--window-icon=/home/dennis/Projects/ptxplus/resources/icons/ptxplus.png "\
												"--height=400 --width=600 --list "\
												"--text={text!r} "\
												"--column='File' --column='Type' --column='Ref' --column='Context' --column='Description' "\
												"--hide-column=1,2".format
						os.system(sed_filter(log='error.log') + ' | ' +
								  dialog_command(title='PtxPlus error log report',
												 text ='A total of {0} errors were found'.format(errrCount)))
					except :
						tools.userMessage('error_manager.py: Error report dialog failed to work!')

				if warnCount == 1 :
					tools.userMessage("Also, one warning was found too")
				elif warnCount > 1 :
					tools.userMessage("A total " + str(warnCount) + " warnings were found too")

				tools.userMessage("For details see: " + self._errorLogFile)

			except :
				tools.userMessage('Unable to open error log file: ' + self._errorLogFile)

		else :
			tools.userMessage('INFO: No errors found.')



	def deleteErrorLog (self) :
		'''Get rid of the error log file.'''

		if os.path.isfile(self._errorLogFile) == True :
			if os.system("rm " + self._errorLogFile) != 0 :
				tools.userMessage("Failed to delete: " + self._errorLogFile)
#        return True


	def recordError (self, event) :
		'''Record an error report line to the error log object.'''


		if os.path.isfile(self._errorLogFile) == True :
			errorWriteObject = codecs.open(self._errorLogFile, "a", encoding='utf_8')
		else :
			errorWriteObject = codecs.open(self._errorLogFile, "w", encoding='utf_8')

		errorWriteObject.write(event + '\n')
		errorWriteObject.close()

