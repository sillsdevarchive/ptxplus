#!/usr/bin/python2.5
# -*- coding: utf-8 -*-
# version: 20080423
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This script will modify an existing map template with map
# data from this project

# 20080925 - djd - Initial draft
# 20081023 - djd - Refactored due to changes in project.conf
# 20081029 - djd - Removed system logging, messages only now
# 20081030 - djd - Added total dependence on log_manager.
#		This script will not run without it because
#		it handles all the parameters it needs.


#############################################################
######################### Load Modules ######################
#############################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil

# Import supporting local classes
from tools import *
from csv import reader
from xml.etree.cElementTree import XMLID, ElementTree

# Instantiate local classes
tools		= Tools()
elementtree	= ElementTree()


class MakeMapFile (object) :

	def main (self, log_manager) :

		# Pull in all the relevant vars and settings
		basePath = os.environ.get('PTXPLUS_BASE')
		mapProject = os.getcwd() + "/" + log_manager._settings['Process']['Paths']['PATH_MAPS']
		mapSource = log_manager._settings['Process']['Paths']['PATH_MAPS_SOURCE']
		mapSource = mapSource.replace( '$(PTXPLUS_BASE)', basePath)
		colorMode = log_manager._settings['General']['MapProcesses']['mapColorMode']
		inputFile = log_manager._currentInput
		(head, tail) = os.path.split(inputFile)
		csvFileName =  mapProject + "/" + tail.replace('.svg', '.csv')
		csvStyleFileName = mapProject + "/styles.csv"
		csvStyleFileSource = mapSource + "/styles.csv"
		svgSourceFile = mapSource + "/" + tail
		csvSourceFile = mapSource + "/" + tail.replace('.svg', '.csv')
		# This may be optional but we'll build a file name for it anyway
		if colorMode == "true" :
#			mapBackgroundImageFile = inputFile.replace('.svg', '-bkgrnd-cl.png')
			mapBackgroundImageFile = tail.replace('.svg', '-bkgrnd-cl.png')
			mapBackgroundImageFileSource = mapSource + "/" + tail.replace('.svg', '-bkgrnd-cl.png')
		else :
			mapBackgroundImageFile = inputFile.replace('.svg', '-bkgrnd-gr.png')
			mapBackgroundImageFileSource = mapSource + "/" + tail.replace('.svg', '-bkgrnd-gr.png')

		print colorMode

		# See if the maps folder exists then check for the files we need.
		if not os.path.isdir(mapProject) :
			os.mkdir(mapProject)

		# Is our input file there? Just because Make told us this doesn't make it so.
		if not os.path.isfile(inputFile) :
			shutil.copy(svgSourceFile, inputFile)

		# Does this map need a background image, is it there?
		if not os.path.isfile(mapBackgroundImageFile) :
			if os.path.isfile(mapBackgroundImageFileSource) :
				shutil.copy(mapBackgroundImageFileSource, mapBackgroundImageFile)

		# How about our data file?
		if not os.path.isfile(csvFileName) :
			shutil.copy(csvSourceFile, csvFileName)

		# And our style file?
		if not os.path.isfile(csvStyleFileName) :
			shutil.copy(csvStyleFileSource, csvStyleFileName)

############################################################################################################################
# There's a problem with working with namespaces. The solution, or at least part of it, migh be if we use
# ElementTree.parse() (or something close to that) which will help it work better with namespaces.
# Another possible solution could be using a call from ElementTree called qname. This might help it
# better keep track of namespaces and get the data needed in the righ place.

		# Open and read XML file
		fhXML = file(inputFile)
		txtXML = ''.join(fhXML)
		fhXML.close
		(eXML, dXML) = XMLID(txtXML)

############################################################################################################################


		# Pull in the CSV map point data
		csvMapData = file(csvFileName)
		mapData = reader(csvMapData, dialect = 'excel')

		# Pull in the CSV style data
		csvStyleData = file(csvStyleFileName)
		styleData = reader(csvStyleData, dialect = 'excel')

		# Gather the new map point data
		map = {}
		for row in mapData:
			if len(row) > 0 and row[0] != "MapPointData" :
				map[row[0]] = row[1]

		# Gather the new style data
		styles = {}
		for row in styleData:
			if row[0] != "StyleName" :
				styles[row[0]] = row[1]

#####################################################################################

		# Replace background image file name (if needed)
# See note above first...
# This does not work yet there is a problem with setting the background image
# file name. It doesn't like xlink:href or something like that.
# Not sure what to do at this point as this seems to be a namespace issue
# which could be a part of a larger issue. For now, the file name of the
# background image has to be set by hand.
		if dXML.has_key('BackgroundImage') :
			dXML['BackgroundImage'].set('xlink:href', mapBackgroundImageFile)

######################################################################################


		# Replace the key fields in the XML data with the new map data
		for key in map.keys() :
			if dXML.has_key(key) :
				dXML[key].text = unicode(map[key], 'utf-8')
				temp = re.sub("_.*$", '', key)
				if styles.has_key(temp) :
					dXML[key].set('style', styles[temp])

		# Overwrite the original SVG file with the new data
		ElementTree(element = eXML).write(inputFile, encoding = 'UTF-8')


# This starts the whole process going
def doIt(log_manager):

	thisModule = MakeMapFile()
	return thisModule.main(log_manager)
