#!/usr/bin/python2
# -*- coding: utf_8 -*-
# version: 20080423
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This script will auto-generate the system make file based
# on settings found in the .conf file. It is supposed to be
# generic and build for the type of publishing project it is.
# It does this every time the typeset file is used with valid
# commands.

# History:
# 20100823 - djd - Initial draft (Started with make_scripture.py)


#############################################################
######################### Load Modules ######################
#############################################################
# Firstly, import all the modules we need for this process

import sys, os, codecs, operator

# Import supporting local classes
import tools


class MakeMakefile (object) :


# FIXME: There are no doubt much leftover code from the make_scripture.py
# that will make this module less then generic. As we find code like this
# it needs to be replaced so this module will work with any recognized
# type in the system.

	def main (self, log_manager) :
		'''This is the main process function for generating the makefile.'''

		self._log_manager = log_manager
		basePath = os.environ.get('PTXPLUS_BASE')
		sourcePath = os.path.abspath(self._log_manager._settings['System']['Paths']['PATH_SOURCE'])

		# Get the type of project this is
		self._projectType = tools.getProjectType()

		# Get some info we will need
		self._pubInfo = tools.getPubInfoObject()

		# The folder name for peripheral material is auto created here
		peripheralFolderName = os.getcwd().split('/')[-1]

		# Create the new makefile object (overwrite the old file)
		# Note here about encoding. If you use utf_8_sig rather than
		# just utf_8 it will put a BOM in the file. This seems to make
		# Make choke. Keeping with just utf_8 seems to fix it.
		makefileObject = codecs.open('.makefile', 'w', encoding='utf_8')

		# Create the file elements
		makefileHeader = "# Makefile\n\n# This is an auto-generated file, do not edit. Any necessary changes\n" + \
				"# should be made to the .scripture.conf file.\n\n"

		# Pull in settings stored in the Process section of the .scripture.conf object
		# As there are sub-sections we will add them to the settings object one
		# at after another. There's probably a better way to do this but not today ;-)
		makefileSettings = ""

		# First grab some individual settings we need in the makefile
		cMapVal = self._log_manager._settings['System']['Processes']['MapProcesses'].get('CREATE_MAP',0)
		makefileSettings = makefileSettings + 'CREATE_MAP=' + cMapVal + '\n'

		rgbPath = self._log_manager._settings['System']['Processes']['MapProcesses'].get('RGB_PROFILE','/usr/share/color/icc/sRGB.icm')
		makefileSettings = makefileSettings + 'RGB_PROFILE=' + rgbPath + '\n'

		cmykPath = self._log_manager._settings['System']['Processes']['MapProcesses'].get('CMYK_PROFILE','/usr/share/color/icc/ISOcoated.icc')
		makefileSettings = makefileSettings + 'CMYK_PROFILE=' + cmykPath + '\n'

		# Get our switches from their respective sections
		useIllustrations = self._log_manager._settings['Format']['Illustrations']['USE_ILLUSTRATIONS']
		makefileSettings = makefileSettings + 'USE_ILLUSTRATIONS=' + useIllustrations + '\n'

		usePlaceholders = self._log_manager._settings['Format']['Illustrations']['USE_PLACEHOLDERS']
		makefileSettings = makefileSettings + 'USE_PLACEHOLDERS=' + usePlaceholders + '\n'

		useWatermark = self._log_manager._settings['Format']['PageLayout']['USE_WATERMARK']
		makefileSettings = makefileSettings + 'USE_WATERMARK=' + useWatermark + '\n'

		useCropmarks = self._log_manager._settings['Format']['PageLayout']['USE_CROPMARKS']
		makefileSettings = makefileSettings + 'USE_CROPMARKS=' + useCropmarks + '\n'

		usePageborder = self._log_manager._settings['Format']['PageLayout']['USE_PAGE_BORDER']
		makefileSettings = makefileSettings + 'USE_PAGE_BORDER=' + usePageborder + '\n'

		useAdjustments = self._log_manager._settings['ProjectText']['WorkingText']['Features']['USE_ADJUSTMENTS']
		makefileSettings = makefileSettings + 'USE_ADJUSTMENTS=' + useAdjustments + '\n'

		# Pickup some other misc settings needed by makefile
		sourceLock = self._log_manager._settings['ProjectText']['SourceText']['LOCKED']
		makefileSettings = makefileSettings + 'LOCKED=' + sourceLock + '\n'

		sourceName = self._log_manager._settings['ProjectText']['SourceText']['NAME_SOURCE_ORIGINAL']
		makefileSettings = makefileSettings + 'NAME_SOURCE_ORIGINAL=' + sourceName + '\n'

		graphicsList = self._log_manager._settings['Format']['Illustrations']['LIST_GRAPHICS']
		c = 0
		makefileSettings = makefileSettings + 'LIST_GRAPHICS='
		for f in graphicsList :
			if c == 0 :
				makefileSettings = makefileSettings + f
				c+=1
			else :
				makefileSettings = makefileSettings + ' ' + f

		makefileSettings = makefileSettings + '\n'

		# Modules used by the makefile, note the use of extra
		# quoting. This is to preserve the strings.
		for key, value, in self._log_manager._settings['System']['Modules'].iteritems() :
			makefileSettings = makefileSettings + key + "=" + value + '\n'

		for key, value, in self._log_manager._settings['System']['Extensions'].iteritems() :
			makefileSettings = makefileSettings + key + "=" + value + '\n'

		# Get our path information and output absolute paths
		for key, value, in self._log_manager._settings['System']['Paths'].iteritems() :
			if value.split('/')[0] == '__PTXPLUS__' :
				makefileSettings = makefileSettings + key + '=' + value.replace('__PTXPLUS__', basePath) + '\n'
			else :
				makefileSettings = makefileSettings + key + '=' + os.path.abspath(value) + '\n'

		# Insert the peripheral folder name here. This is a
		# hard-coded insert because it should always be the
		# name given here. The user cannot change this.
		makefileSettings = makefileSettings + 'PATH_SOURCE_PERIPH=' + sourcePath + '/' + peripheralFolderName + '\n'

		# We will use a function to tell us what the project
		# config name is.
		makefileSettings = makefileSettings + 'FILE_PROJECT_CONF=' + tools.getProjectConfigFileName() + '\n'

		for key, value, in self._log_manager._settings['System']['Files'].iteritems() :
			makefileSettings = makefileSettings + key + "=" + value + '\n'

		for key, value, in self._log_manager._settings['System']['TeX'].iteritems() :
			makefileSettings = makefileSettings + key + "=" + value + '\n'

		# Build up all the component groupings

		# Build component groups
		makefileSettings += '\n'.join(key + '=' + ' '.join(value) for key, value in self._log_manager._settings['Format']['Binding'].iteritems()) + '\n'

		# Build meta groups here
		makefileSettings += '\n'.join(key + '=' + ' '.join(value) for key, value in self._pubInfo['BindingGroups'].iteritems()) + '\n'

		# Get special file names for this publication type
		for key, value in self._pubInfo['FileNames'].iteritems() :
			makefileSettings += key + "=" + value + '\n'

#        makefileSettings += 'FILE_BOOK=BOOK.pdf\n'
#        makefileSettings += 'FILE_GROUP_CONTENT_PDF=GROUP_CONTENT.pdf\n'
#        #
#        makefileSettings += 'FILE_GROUP_CONTENT_TEX=GROUP_CONTENT.tex\n'

		# Output the helper commands
		for key, value, in self._log_manager._settings['System']['HelperCommands'].iteritems() :
			makefileSettings += key + "=" + value + '\n'

		# Add component mapping info here
		editor = self._log_manager._settings['ProjectText']['SourceText']['Features'].get('projectEditor')

		# Build filter list of all possible components in this project
		# The following would work to build the initial list:
		# filterList = []
		# for list in self._log_manager._settings['Format']['Binding'].itervalues() :
		#     filterList.extend(list)
		# However, using reduce is a much faster way. Note the '[]' a the end of the
		# line. This initializes the filterList.
		filterList = reduce(operator.add, self._log_manager._settings['Format']['Binding'].itervalues(), [])

		for cID in filterList :
			makefileSettings += tools.getComponentNameKey(cID) + '=' + tools.getComponentNameValue(cID) + '\n'

		# Create the final key/values for the file
		makefileFinal = ""

		# Add in system level include files first, then the component types
		makefileFinal += "include " + basePath + "/bin/make/lib_" + self._projectType + "/system.mk\n"

		for value in self._pubInfo['Components']['componentTypeList'] :
			makefileFinal += "include " + basePath + "/bin/make/lib_" + self._projectType + "/" + value + ".mk\n"

		# Output to the new makefile file
		makefileObject.write(makefileHeader + makefileSettings + makefileFinal)

# This starts the whole process going
def doIt(log_manager):
	thisModule = MakeMakefile()
	return thisModule.main(log_manager)
