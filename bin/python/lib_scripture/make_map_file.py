#!/usr/bin/python
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
		mapProject = log_manager._settings['Process']['Paths']['PATH_MAPS']
		mapSource = log_manager._settings['Process']['Paths']['PATH_MAPS_SOURCE']
		mapSource = mapSource.replace( '$(PTXPLUS_BASE)', "")
		inputFile = log_manager._currentInput
		csvFileName = inputFile.replace('.svg', '.csv')
		(head, tail) = os.path.split(csvFileName)
		csvStyleFileName = head + "/styles.csv"
		csvStyleFileSource = basePath + "/" + mapProject + "/styles.csv"
		svgSourceFile = basePath + mapSource + "/" + os.path.basename(inputFile)
		csvSourceFile = basePath + mapSource + tail

		# See if the maps folder exists then check for the files we need.
		if not os.path.isdir(mapProject) :
			os.mkdir(mapProject)

		# Is our input file there? Just because Make told us this doesn't make it so.
		if not os.path.isfile(inputFile) :
			shutil.copy(svgSourceFile, inputFile)

		# How about our data file?
		if not os.path.isfile(csvFileName) :
			shutil.copy(csvSourceFile, csvFileName)

		# And our style file?
		if not os.path.isfile(csvStyleFileName) :
			shutil.copy(csvStyleFileSource, csvStyleFileName)

		# Open and read XML file
		fhXML = file(inputFile)
		txtXML = ''.join(fhXML)
		fhXML.close
		(eXML, dXML) = XMLID(txtXML)

		# Pull in the CSV map point data
		csvMapData = file(csvFileName)
		mapData = reader(csvMapData, dialect = 'excel')

		# Pull in the CSV style data
		csvStyleData = file(csvStyleFileName)
		styleData = reader(csvStyleData, dialect = 'excel')

		# Gather the new map point data
		map = {}
		for row in mapData:
			if row[0] != "MapPointData" :
				map[row[0]] = row[1]

		# Gather the new style data
		styles = {}
		for row in styleData:
			if row[0] != "StyleName" :
				styles[row[0]] = row[1]

# Note how to do a replace in re: res = re.sub("Style_", "", row[0])

		# Replace the key fields in the XML data with the new map data
		for key in map.keys() :
			if dXML.has_key(key) :
				dXML[key].text = unicode(map[key], 'utf-8')
				temp = re.sub("_.*$", '', key)
#				print key, temp
				if styles.has_key(temp) :
					dXML[key].set('style', styles[temp])

		# Overwrite the original SVG file with the new data
		ElementTree(element = eXML).write(inputFile, encoding = 'UTF-8')


# This starts the whole process going
def doIt(log_manager):

	thisModule = MakeMapFile()
	return thisModule.main(log_manager)
