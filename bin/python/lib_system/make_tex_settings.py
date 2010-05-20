#!/usr/bin/python
# -*- coding: utf-8 -*-
# version: 20100516
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This script will auto-generate the TeX macro setup file.
# It will define the document to the ptx2pdf macro system and
# will include things like page size, columns, etc. A custom
# settings file will be linked to this one that will contain
# special tweaks for individual projects.

# History:
# 20100516 - djd - Initial draft


#############################################################
######################### Load Modules ######################
#############################################################
# Firstly, import all the modules we need for this process

import sys, os, codecs

# Import supporting local classes
from tools import *
tools = Tools()


class MakeTexSettings (object) :


	def main (self, log_manager) :
		'''This is the main process function for generating the TeX setup file.
			Some of the settings will be found in the control file as they need
			to be associated with the object that is being processed.'''

		log_manager = log_manager
		log_manager._currentSubProcess = 'MkTexSettings'

		# Build some paths and file names
		texMacros = log_manager._settings['Process']['Files'].get('FILE_TEX_MACRO', 'paratext2.tex')
		setupFile = os.getcwd() + "/" + log_manager._settings['Process']['Files'].get('FILE_TEX_SETUP', 'auto-tex.txt')
		customSetup = os.getcwd() + "/" + log_manager._settings['Process']['Files'].get('FILE_TEX_SETUP_CUSTOM', 'custom-tex.txt')
		styleFile = os.getcwd() + "/" + log_manager._settings['Process']['Files'].get('FILE_TEX_STYLE', 'project.sty')

		# Bring in page format settings
		cropmarks = log_manager._settings['Format']['PageLayout'].get('CROPMARKS', 'true')
		pageHeight = log_manager._settings['Format']['PageLayout'].get('pageHeight', '210mm')
		pageWidth = log_manager._settings['Format']['PageLayout'].get('pageWidth', '148mm')
\endbooknoejecttrue (endBookNoEject)
# Columns
\TitleColumns=1
\IntroColumns=1
\BodyColumns=2
\def\ColumnGutterFactor{15}
\ColumnGutterRuletrue
\ColumnGutterRuleSkip=4pt
# Margins
\MarginUnit=12mm
\def\TopMarginFactor{1.75}
\def\BottomMarginFactor{0} - if set to 0 it will not show up in the output
\def\SideMarginFactor{1.0}
\BindingGutter=12mm
\BindingGuttertrue (useBindingGutter)
# HeaderFooter
\def\HeaderPosition{.75}
\def\FooterPosition{.5}
# Fonts
\def\regular{"[../Fonts/CharisSIL/CharisSILR.ttf]/GR"}
\def\bold{"[../Fonts/CharisSIL/CharisSILB.ttf]/GR"}
\def\italic{"[../Fonts/CharisSIL/CharisSILI.ttf]/GR"}
\def\bolditalic{"[../Fonts/CharisSIL/CharisSILBI.ttf]/GR"}


		# Create the file header
		header = "% tex_settings.txt\n\n% This is an auto-generated file, do not edit. Any necessary changes\n" + \
				"% should be made to the project.conf file or the custom TeX setup file.\n\n"


		# Output to the new makefile file
		# Create the new TeX settings object (overwrite the old file)
		settingsFileObject = codecs.open(setupFile, 'w', encoding='utf_8_sig')
		settingsFileObject.write(header)
		# This connects the system with the custom macro code
		settingsFileObject.write('\\input ' + texMacros + '\n')
		# Add page format settings
		settingsFileObject.write('\\PaperHeight=' + pageHeight + '\n')
		settingsFileObject.write('\\PaperWidth=' + pageWidth + '\n')



		# Now put out the custom macro file path (this may need to be moved)
		settingsFileObject.write('\\input ' + customSetup + '\n')
		# Add some format features here
		if cropmarks.lower() == 'true' :
			settingsFileObject.write('\\CropMarkstrue\n')

		# Add the global style sheet
		settingsFileObject.write('\\stylesheet{' + styleFile + '}\n')
		settingsFileObject.close()


# This starts the whole process going
def doIt(log_manager):
	thisModule = MakeTexSettings()
	return thisModule.main(log_manager)
