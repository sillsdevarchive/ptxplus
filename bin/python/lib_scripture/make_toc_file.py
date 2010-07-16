#!/usr/bin/python2
# -*- coding: utf_8 -*-
# version: 20100514
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This class will create the table of contents from ptx2pdf
# TeX output. It assumes:
#    1) Found in all rows are these markers: \tr \tc1 \tcr2
#    2) Output is to this format: \tbltwowlrow{BookName}{pg}
#
# Initial implementation is going to be pretty simple and
# will be built on as we go.

# History:
# 20100514 - djd - Initial draft


#############################################################
#################### Initialize The Process #################
#############################################################
# Firstly, import all the standard Python modules we need for
# this process

#import os, sys, codecs, csv, shutil, operator
import os, sys, codecs, shutil

# Import supporting local classes
#from tools import *
#tools = Tools()

class MakeTocFile (object) :

	# Intitate the whole class
	def __init__(self, log_manager) :

		self._settings = log_manager._settings
		self._log_manager = log_manager
		self._log_manager._currentSubProcess = 'MakeTocFile'
		self._texTocFile = log_manager._currentInput
		self._bookID = log_manager._currentTargetID
		self._outputFile = log_manager._currentOutput
		self._outFileObject = {}




	def main(self):
		'''We will open up our content file which should be Unicode
			encoded and in SFM format. If that file doesn't exsist
			then we need to gracefully stop at that point. This will
			prevent other processes from crashing.'''

		# Collect the settings we need
		mainTitle = self._settings['Process']['TOC'].get('mainTitle','Table of Contents')
		headerRowBookTitle = self._settings['Process']['TOC'].get('headerRowBookTitle','tr')
		headerRowBookAbbr = self._settings['Process']['TOC'].get('headerRowBookAbbr','tr')
		headerRowPageNum = self._settings['Process']['TOC'].get('headerRowPageNum','tr')
		columnFormat = self._settings['Process']['TOC'].get('columnFormat','twoColumnLeadered')
		inputRowMarker = self._settings['Process']['TOC'].get('inputRowMarker','tr')
		inputColOne = self._settings['Process']['TOC'].get('inputColOne','tc1')
		inputColTwo = self._settings['Process']['TOC'].get('inputColTwo','tcr2')
		inputColThree = self._settings['Process']['TOC'].get('inputColThree','tcr3')

		# Build some vars in context
		tocRowFormatMarker = ''
		tocHeaderRow = ''

		if columnFormat == 'twoColumnLeadered' :
			tocRowFormatMarker = '\\tbltwowlrow'
			# While we are here build the header row
			tocHeaderRow = "\\tbltwowlheader{" + headerRowBookTitle + "}{" + headerRowPageNum + "}" + "\n"
		elif columnFormat == 'threeColumnLeadered' :
			tocRowFormatMarker = '\\tblthreewlrow'
			# Build the header row
			tocHeaderRow = "\\tblthreewlheader{" + headerRowBookTitle + "}{" + headerRowBookAbbr + "}{" + headerRowPageNum + "}" + "\n"
		else :
			self._log_manager.log("ERRR", "Improper TOC format given in project.conf file. It is not supported by this process")
			return

		if os.path.isfile(self._texTocFile) :
			inFileObject = codecs.open(self._texTocFile, "r", encoding='utf_8')
		else :
			# If we don't have a SFM toc input file we're done now.
			self._log_manager.log("ERRR", "The [" + self._texTocFile + "] file does not exist so the process has been halted.")
			return

		if os.path.isfile(self._outputFile) :
			# If the output file exists we will not go through with the process
			# The user will need to manually verify and delete the file if
			# that is warrented before this process can be run again. This is
			# to prevent lost of work that may have been done to the TOC file.
			self._log_manager.log("INFO", "The " + self._outputFile + " exists so the process is being skipped.")

		else :

			# Everything is in place and we can move forward now

			# Create header information for this sfm file
			headerInfo = "\\id OTH\n" + \
				"\\ide UTF-8\n" + \
				"\\periph " + self._bookID + "\n" + \
				"\\mt1 " + mainTitle + "\n" + \
				"\\p \n" + \
				"\\makedigitsother\\catcode`{=1 \\catcode`}=2\n" + \
				"\\baselineskip=12pt\n" + \
				tocHeaderRow

			# Create the toc content from the input file
			content = ""
			for row in inFileObject :
				row = row.split('\\')
				if row[1].strip() == inputRowMarker :
					if columnFormat == 'twoColumnLeadered' :
						bookName = row[2].replace(inputColOne, '').strip()
						pageNum = row[3].replace(inputColTwo, '').strip()
						content = content + tocRowFormatMarker + "{" + bookName + "}{" + pageNum + "}" + "\n"
# This next elif is not tested, take this out when it is
					elif columnFormat == 'tblthreewlrow' :
						bookName = row[2].replace(inputColOne, '').strip()
						bookAbbr = row[3].replace(inputColTwo, '').strip()
						pageNum = row[4].replace(inputColThree, '').strip()
						content = content + tocRowFormatMarker + "{" + bookName + "}{" + bookAbbr + "}{" + pageNum + "}" + "\n"
					else :
						self._log_manager.log("ERRR", "The [" + columnFormat + "] is not a valid format so the process has been halted.")
						return

			# Build the toc file footer
			footerInfo = "\\catcode`{=11\\catcode`}=11\\makedigitsletters\n"

			# Now we need output anything we might have collected. If nothing was
			# found, just output the header.
			self._outFileObject = codecs.open(self._outputFile, "w", encoding='utf_8')
			self._outFileObject.write(headerInfo)
			self._outFileObject.write(content)
			self._outFileObject.write(footerInfo)
			self._log_manager.log("DBUG", "Created file and wrote out to: " + self._outputFile)

			# Close the piclist file
			self._outFileObject.close()



# This starts the whole process going
def doIt(log_manager):

	thisModule = MakeTocFile(log_manager)
	return thisModule.main()
