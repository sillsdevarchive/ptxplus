#!/usr/bin/python2.5
# -*- coding: utf-8 -*-
# version: 20080423
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu) it may not work right
# with earlier versions.

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This script will modify an existing map template with map data from this
# project

# 20080925 - djd - Initial draft
# 20081023 - djd - Refactored due to changes in project.conf
# 20081029 - djd - Removed system logging, messages only now
# 20081030 - djd - Added total dependence on log_manager.  This script will not
# run without it because it handles all the parameters it needs.
# 20090909 - te - Fixed bug in XML namespaces and a path problem in a copy
# routine
# 20090914 - djd - Removed code that was duplicating makefile functions like
# creating the Maps folder, etc.
# 20110516 - djd - Modify to handle master data file for map data.


###############################################################################
################################## Load Modules ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil, re

# Import supporting local classes
#from tools import *
import tools
from csv import reader
from xml.etree.ElementTree import XMLID, ElementTree

# Instantiate local classes
#tools        = Tools()
elementtree    = ElementTree()


class MakeMapFile (object) :

	def main (self, log_manager) :

		# Pull in all the relevant vars and settings
		# FIXME: Might want to replace hard coded extentions with system vars
		# for file types
		basePath        = os.environ.get('PTXPLUS_BASE')
		mapProject      = os.getcwd() + "/" + tools.pubInfoObject['Paths']['PATH_MAPS']
		colorSpace      = log_manager._settings['Format']['MapProcesses']['colorSpace']
		inputFile       = log_manager._currentInput
		outputFile      = log_manager._currentOutput
		(head, tail)    = os.path.split(outputFile)
		mapSetType      = tail[0]
		mapID           = tail.replace('.svg', '')
		dataFileName    = mapProject + "/" + mapSetType + "00-data.csv"
#        dataFileName    = mapProject + "/" + tail.replace('.svg', '-data.csv')
		styleFileName   = mapProject + "/" + tail.replace('.svg', '-style.csv')
		backgroundFile  = tail.replace('.svg', '-bkgrnd-' + colorSpace.split()[1].lower() + '.png')


###############################################################################
# There's a problem with working with namespaces.  The solution, or at least
# part of it, migh be if we use ElementTree.parse() (or something close to that)
# which will help it work better with namespaces.  Another possible solution
# could be using a call from ElementTree called qname.  This might help it
# better keep track of namespaces and get the data needed in the righ place.
# For now we use XMLID to pull out the element tag names so we can work with
# them and change the data. For more info on ElementTree go to:
# http://docs.python.org/library/xml.etree.elementtree.html#the-element-interface


		# Open and read XML file
		fhXML = file(inputFile)
		txtXML = ''.join(fhXML)
		fhXML.close
		(eXML, dXML) = XMLID(txtXML)

###############################################################################


		# Pull in the CSV map point data
		csvMapData = file(dataFileName)
		mapData = reader(csvMapData, dialect = 'excel')

		# Pull in the CSV style data
		csvStyleData = file(styleFileName)
		styleData = reader(csvStyleData, dialect = 'excel')

		# Gather the new map point data
		map = {}
		for row in mapData:
			if len(row) > 0 and row[0] != "MapPointID" :
				if row[3].find(mapID) != -1 :
					map[row[0]] = row[2]

		# To get the right background file image, we need to insert the key and
		# file name into the style data list.  Encode the backgroundFile string
		# to be Unicode utf-8
#        map['background'] = backgroundFile.encode('utf-8')

		# Gather the new style data
		styles = {}
		for row in styleData:
			if len(row) > 0 and row[0] != "StyleName" :
				styles[row[0]] = row[1]

		# FIXME: To get the right background file image, we need to insert the key and
		# file name into the style data list.  Encode the backgroundFile string
		# to be Unicode utf-8
#        styles['background'] = backgroundFile.encode('utf-8')

		# Replace the key fields in the XML data with the new map data
		for key in map.keys() :
			if dXML.has_key(key) :
				dXML[key].text = unicode(map[key], 'utf-8')
				temp = re.sub("_.*$", '', key)
				# Set the style for each map point key
				if styles.has_key(temp) :
					dXML[key].set('style', styles[temp])


		# FIXME: Set the background once
#        if dXML.has_key('background') :
#            dXML['background'].image = unicode(map[key], 'utf-8')
#            dXML['background'].set('href', backgroundFile.encode('utf-8'))

		# Overwrite the original SVG file with the new data
		ElementTree(element = eXML).write(outputFile, encoding = 'UTF-8')


# This starts the whole process going
def doIt(log_manager):

	thisModule = MakeMapFile()
	return thisModule.main(log_manager)
