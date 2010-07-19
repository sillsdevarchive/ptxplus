#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20090118
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This script will create a simple backup file that will be
# put in the root of the project. This serves kind of like a
# one-step undo, no more than that.

# History:
# 20090118 - djd - Initial draft


#############################################################
######################### Load Modules ######################
#############################################################
# Firstly, import all the modules we need for this process

import sys, tarfile

# Import supporting local classes
from tools import *
tools = Tools()

# Pull in the name of the template file name
templateName = sys.argv[1]


class MakeTemplate (object) :


	def main (self, templateName) :
		'''Here we will manage the template making process.'''

		self.settings = tools.getSettingsObject()

		# For the location we use whatever the makefile.conf file has
		# whether it is abs or relative. Note, we use abs in archive_project.py
		templateFilePath = self.settings['Process']['Paths']['PATH_TEMPLATES']
		templateFile = templateFilePath + "/" + templateName + ".tar.gz"

		# Let's look to see if the Template folder is there
		if not os.path.isdir(templateFilePath) :
			os.mkdir(templateFilePath)

		tar = tarfile.open(templateFile, 'w:gz')
		# We only want to add project settings files to the template so
		# we will only take the files in the root of the project (all
		# except the Makefile file).

		# how do we do this??????????????????
		tar.add(???)

		tar.close()

		# Tell the world what we did
		tools.userMessage('A template has been made from the current project settings')


# This starts the whole process going
def doIt():

	thisModule = MakeTemplate()
	return thisModule.main(templateName)
