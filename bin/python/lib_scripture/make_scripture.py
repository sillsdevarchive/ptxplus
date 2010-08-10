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
# on settings found in the .scripture.cfg file. It does this
# every time the typeset file is used with valid commands.

# History:
# 20080806 - djd - Initial draft
# 20081023 - djd - Refactor .project.conf structure changes
# 20081028 - djd - Removed system logging, messages only now
# 20090218 - djd - Added system logging access as other like
#       processes needed it too
# 20100513 - djd - Added key/value harvesting for Process::Files
# 20100712 - djd - Changed the way lists work in the binding
#       area so a proper list could be used in the .conf file.


#############################################################
######################### Load Modules ######################
#############################################################
# Firstly, import all the modules we need for this process

import sys, os, codecs

# Import supporting local classes
import tools


class MakeMakefile (object) :


	def main (self, log_manager) :
		'''This is the main process function for generating the makefile.'''

		self._log_manager = log_manager
		basePath = os.environ.get('PTXPLUS_BASE')
		sourcePath = os.path.abspath(self._log_manager._settings['System']['Paths']['PATH_SOURCE'])


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

		for key, value, in self._log_manager._settings['System']['Files'].iteritems() :
			makefileSettings = makefileSettings + key + "=" + value + '\n'

		for key, value, in self._log_manager._settings['System']['TeX'].iteritems() :
			makefileSettings = makefileSettings + key + "=" + value + '\n'

		# Build up all the component groupings
		# The tricky part here is that we are
		# going to output to the makefile hard-coded
		# file names to simplify rules. We need
		# to be sure we have covered every .conf
		# setting necessary rather than relying on
		# an iteration to catch everything.

		# Cover components
		cvMatter = ''
		cvGroup = ''
		for fn in self._log_manager._settings['Format']['Binding']['MATTER_COVER'] :
			cvMatter = cvMatter + fn + ' '
			cvGroup = cvGroup + fn + '.pdf '

		# Build content components
		otComponents = ''
		for fid in self._log_manager._settings['Format']['Binding']['MATTER_OT'] :
			otComponents = otComponents + fid + ' '

		ntComponents = ''
		for fid in self._log_manager._settings['Format']['Binding']['MATTER_NT'] :
			ntComponents = ntComponents + fid + ' '

		apComponents = ''
		for fid in self._log_manager._settings['Format']['Binding']['MATTER_AP'] :
			apComponents = apComponents + fid + ' '

		# Build peripheral components
		frMatter = ''
		frGroup = ''
		for fn in self._log_manager._settings['Format']['Binding']['MATTER_FRONT'] :
			frMatter = frMatter + fn + ' '
			frGroup = frGroup + fn + '.pdf '

		bkMatter = ''
		bkGroup = ''
		for fn in self._log_manager._settings['Format']['Binding']['MATTER_BACK'] :
			bkMatter = bkMatter + fn + ' '
			bkGroup = bkGroup + fn + '.pdf '

		mpMatter = ''
		mpGroup = ''
		for fn in self._log_manager._settings['Format']['Binding']['MATTER_MAPS'] :
			mpMatter = mpMatter + fn + ' '
			mpGroup = mpGroup + fn + '.pdf '

		# Output component matter
		makefileSettings = makefileSettings + 'MATTER_COVER=' + cvMatter.strip() + '\n'
		makefileSettings = makefileSettings + 'MATTER_OT=' + otComponents.strip() + '\n'
		makefileSettings = makefileSettings + 'MATTER_NT=' + ntComponents.strip() + '\n'
		makefileSettings = makefileSettings + 'MATTER_AP=' + apComponents.strip() + '\n'
		makefileSettings = makefileSettings + 'MATTER_FRONT=' + frMatter.strip() + '\n'
		makefileSettings = makefileSettings + 'MATTER_BACK=' + bkMatter.strip() + '\n'
		makefileSettings = makefileSettings + 'MATTER_MAPS=' + mpMatter.strip() + '\n'

		# Output the groups here
		contentGroup = otComponents + ' ' + ntComponents + ' ' + apComponents
		makefileSettings = makefileSettings + 'GROUP_COVER=' + cvGroup.strip() + '\n'
		makefileSettings = makefileSettings + 'GROUP_FRONT=' + frGroup.strip() + '\n'
		makefileSettings = makefileSettings + 'GROUP_CONTENT=' + contentGroup.strip() + '\n'
		makefileSettings = makefileSettings + 'GROUP_BACK=' + bkGroup.strip() + '\n'
		makefileSettings = makefileSettings + 'GROUP_MAPS=' + mpGroup.strip() + '\n'

		# Make the master book file name (hard codded)
		makefileSettings = makefileSettings + 'FILE_BOOK=BOOK.pdf\n'


		makefileSettings = makefileSettings + 'FILE_GROUP_CONTENT_PDF=GROUP_CONTENT.pdf\n'

		# Make the content group TeX control file (hard codded)
		# The other groups will not use TeX to compile their master
		# PDF file like the content group does. They will use pdftk
		# so a control file is not necessary.
		makefileSettings = makefileSettings + 'FILE_GROUP_CONTENT_TEX=GROUP_CONTENT.tex\n'

		# Output the helper commands
		for key, value, in self._log_manager._settings['System']['HelperCommands'].iteritems() :
			makefileSettings = makefileSettings + key + "=" + value + '\n'

		# Add make rule files via the include call in make
		# This is all controled via the .scripture.conf file
		basePath = os.environ.get('PTXPLUS_BASE')
		makefileFinal = "include " + basePath + "/bin/make/" + self._log_manager._settings['System']['MakefileSettings']['MakeIncludeVariables'][self._log_manager._settings['ProjectText']['SourceText']['Features']['projectEditor']] + '\n'

		for key, value, in self._log_manager._settings['System']['MakefileSettings']['MakeInclude'].iteritems() :
			makefileFinal = makefileFinal + "include " + basePath + "/bin/make/" + value + '\n'

		# Output to the new makefile file
		makefileObject.write(makefileHeader + makefileSettings + makefileFinal)

# This starts the whole process going
def doIt(log_manager):
	thisModule = MakeMakefile()
	return thisModule.main(log_manager)
