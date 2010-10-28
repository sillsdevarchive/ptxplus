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
# 20090909 - te - Fixed bug in XML namespaces and a path
#		problem in a copy routine
# 20090914 - djd - Removed code that was duplicating makefile
#		functions like creating the Maps folder, etc.


#############################################################
######################### Load Modules ######################
#############################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil

# Import supporting local classes
#from tools import *
import tools
from csv import reader
from xml.etree.ElementTree import XMLID, ElementTree

# Instantiate local classes
#tools		= Tools()
elementtree	= ElementTree()


class MakeMapFile (object) :

	def main (self, log_manager) :

		# Pull in all the relevant vars and settings
		basePath = os.environ.get('PTXPLUS_BASE')
		mapProject = os.getcwd() + "/" + tools.pubInfoObject['Paths']['PATH_MAPS']
		mapSource = tools.pubInfoObject['Paths']['PATH_RESOURCES_MAPS']
		mapSource = mapSource.replace( '$(PTXPLUS_BASE)', basePath)
		colorMode = log_manager._settings['Format']['MapProcesses']['colorSpace']
		inputFile = log_manager._currentInput
		(head, tail) = os.path.split(inputFile)
		csvFileName =  mapProject + "/" + tail.replace('.svg', '.csv')
		csvStyleFileName = mapProject + "/map-styles.csv"
		csvStyleFileSource = mapSource + "/map-styles.csv"
		svgSourceFile = mapSource + "/" + tail
		csvSourceFile = mapSource + "/" + tail.replace('.svg', '.csv')
		# This may be optional but we'll build a file name for it anyway
		# Where this falls down is when the illustration is greyscale but the project
		# calls for color. The work-around for now is to make the svg file work with
		# both kinds.
		if colorMode == "true" :
			mapBackgroundImageFile = tail.replace('.svg', '-bkgrnd-cl.png')
			mapBackgroundImageFileSource = mapSource + "/" + tail.replace('.svg', '-bkgrnd-cl.png')
		else :
			mapBackgroundImageFile = inputFile.replace('.svg', '-bkgrnd-gr.png')
			mapBackgroundImageFileSource = mapSource + "/" + tail.replace('.svg', '-bkgrnd-gr.png')

		# Does this map need a background image, is it there?
		if not os.path.isfile(mapBackgroundImageFile) :
			if os.path.isfile(mapBackgroundImageFileSource) :
				shutil.copy(mapBackgroundImageFileSource, mapProject + "/" + mapBackgroundImageFile)


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
# In the syntax below using set() it is important to use the {} around the
# name for it to be generated right. See:
# http://docs.python.org/library/xml.etree.elementtree.html#the-element-interface
# for more info.

		if dXML.has_key('BackgroundImage') :
			dXML['BackgroundImage'].set('{http://www.w3.org/1999/xlink}href', mapBackgroundImageFile)

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
