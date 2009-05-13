#!/usr/bin/python2.5
# -*- coding: utf-8 -*-
# version: 20090113
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# Topical Index processing: This will apply final touches
# topical index data that will be typeset. These are things
# such as inserting NBSPs in refs and any other necessary
# text modifications.

# History:
# 20090513 - djd - Initial draft, it is very simple at this
#		point and there is no event logging yet.


#############################################################
######################### Shell Class #######################
#############################################################

import codecs
import parse_sfm

# Import supporting local classes
from tools import *
tools = Tools()


class ProcessTopicIndex (object) :

	def main (self, log_manager) :

		newIndexFile = log_manager._currentOutput

		# Get our book object
		indexObject = "".join(codecs.open(log_manager._currentInput, "r", encoding='utf-8'))

		# Load in the parser
		parser = parse_sfm.Parser()

		# This calls a version of the handler which strips out everything
		# but the text and basic format.
		parser.setHandler(ProcessTopicIndexHandler(log_manager))
		newIndexOutput = parser.transduce(indexObject)

		# Output the modified book file
		newBookObject = codecs.open(newIndexFile, "w", encoding='utf-8')
		newBookObject.write(newIndexOutput)


class ProcessTopicIndexHandler (parse_sfm.Handler) :
	'''This class replaces the Handler class in the parse_sfm module.'''

	def __init__(self, log_manager) :

		self._log_manager = log_manager
		self._book = ""


	def start (self, tag, num, info, prefix) :
		'''This tells us when a tag starts. We will use this information to set location
			and trigger events.'''

		if num != "" :
			return "\\" + tag + " " + num
		else :
			return "\\" + tag

	def text (self, text, tag, info) :
		'''This function allows us to harvest the text from a given text element. This will
			be used to check for quotes.'''

		# Get the book id for setting our location in start()
		if tag == 'id' :
			self._book = text

		# If it is a note we may want to make some changes
		if tag == 'ipi' :
			# Get rid of the last \n if there is on
			if text[-1] == "\n" :
				text = text[:-1]

			# This next line does the replace on the refs that are in the \im field.
			# The first set changes all spaces to NBSPs. The second one changes \n to
			# ', ' (comma + space). Right now this is hardcoded and it may need to
			# have that be a parameter in the .conf file as we go along further
			# The last translate (0x000D:None) is there to replace Windows carage returns.
			newText = unicode(text).translate({0x0020:0x00A0, 0x000A:u', ', 0x000D:None})
			return newText + "\n"

		else :
			return text


	def end (self, tag, ctag, info) :
		'''This function tells us when an element is closed. We will
			use this to mark the end of events.'''

		# Is this a real closing tag?
		if tag + "*" == ctag :
			return "\\" + ctag


	def error (self, tag, text, msg) :
		'''Send any errors the parser finds back to the calling application.'''

		# These are paser errors that should have been dealt with in the sfm checker
		# we will ignore them here.
		# self._log_manager.log("ERRR", msg + "Marker [\\" + tag + "]")
		pass


# This starts the whole process going
def doIt (log_manager) :

	thisModule = ProcessTopicIndex()
	return thisModule.main(log_manager)
