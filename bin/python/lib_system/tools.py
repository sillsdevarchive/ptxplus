#!/usr/bin/python2
# -*- coding: utf_8 -*-
# version: 20080622
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This class will handle basic system functions that are
# common to many scripts.

# History:
# 20080626 - djd - Initial draft
# 20081022 - djd - Folded the config files together and
#        changed the routines here to reflect that
# 20081023 - djd - Refactor .project.conf structure changes
# 20081028 - djd - Moved localiseFontsConf to font_manager.py
# 20091009 - te - Added "No Context" return to getSliceOfText()
# 20100416 - djd - Added CSVtoDict class written by te.
# 20100623 - djd - Added getModuleArguments() function
# 20100625 - djd - Changed utf_8_sig to just utf_8 for all
#       inernal files.
# 20100630 - djd - Refactor for multiple .conf files.


#############################################################
#################### Initialize The Process #################
#############################################################
# Firstly, import all the modules we need for this process

import re, os, shutil, codecs, csv, sys
from configobj import ConfigObj
from datetime import *
#from log_manager import *

class Tools (object) :
	'''This class contains a bunch of misc. functions that work with
		ptxplus. If something can be used cross-scripts, it ends
		up here.'''


	def thisProjectConf (self) :
		'''Look for and return the name of a valid .conf file in
			the current cwd. If not it will simply return the
			string, none'''

		if os.access('.scripture.conf', os.R_OK) :
			return '.scripture.conf'
		elif  os.access('.dictionary.conf', os.R_OK) :
			return '.dictionary.conf'
		else :
			return 'none'


	def taskRunner (self, log_manager, thisTask) :
		'''This is the final function used for running all system tasks.
			All calls from the system to run a task or process should
			end up here.'''

		# Tell the log what we're doing.
		log_manager.log("DBUG", "INFO: Starting process: " + thisTask)

		if log_manager._settings['System']['General'].get('debugMode', 'false').lower() == 'true' :
			# Import the module
			module = __import__(thisTask, globals(), locals(), [])
			log_manager.log("DBUG", "Imported module: " + thisTask)
			# Run the module
			module.doIt(log_manager)
			log_manager.log("DBUG", "Completed: " + thisTask)

		else :
			# If we are in debug mode then do it like this to suppress debugging code

			# Import/load the module
			try :
				module = __import__(thisTask, globals(), locals(), [])
				log_manager.log("DBUG", "Imported module: " + thisTask)
			except :
				self.userMessage("ERROR: Hmmm, cannot seem to import the \"" + thisTask + "\" module. This will not bode well for the rest of the process.")
				log_manager.log("ERRR", "Could not import module: " + thisTask)

			# Run the module
			try :
				module.doIt(log_manager)
				log_manager.log("DBUG", "Process completed: " + thisTask)
			except :
				self.userMessage("ERROR: Cannot run the \"" + thisTask + "\" module.")
				log_manager.log("ERRR", "Cannot run the \"" + thisTask + "\" module.")


	def makeNecessaryFiles (self, path, projType) :
		'''Create all the necessary files and folders for a project.
			If they already exist, we will not touch the existings ones.
			This is driven from the info we get from the ptxplus.conf
			file in the system. It is only for basic project structure.
			For project asset management see the check_assets.py script.'''

		object = self.getSystemSettingsObject()
		fileLib = os.environ.get('PTXPLUS_BASE') + "/resources/lib_sysFiles"

		# FIXME: Might want a more clever way to do this to avoide hard file names
		# FIXME: Might also want error checking on the copy
		# Bring in the .conf file according to the type of project this is
		# but only if it doesn't already exist
		if projType == 'scripture' :
			if not os.access(path + "/.scripture.conf", os.R_OK) :
				shutil.copy(fileLib + "/.scripture.conf", path + "/.scripture.conf")
		elif projType == 'dictionary' :
			if not os.access(path + "/.dictionary.conf", os.R_OK) :
				shutil.copy(fileLib + "/.dictionary.conf", path + "/.dictionary.conf")
		else :
			self.userMessage("ERROR: The project type: [" + projType + "] is unknown. Process halted!")
			sys.exit(1)

		# Make whatever folders are necessary
		for key, folder in object['ProjectStructure']['Folders'].iteritems() :
			if not os.path.isdir(path + '/' + folder) :
				os.mkdir(path + '/' + folder)
				self.userMessage('INFO: Added folder: ' + path + '/' + folder)

		# Now add whatever files we might need
		for key, file in object['ProjectStructure']['Files'].iteritems() :
			if not os.path.isfile(file) :
				shutil.copy(fileLib + "/" + file, file)
				self.userMessage('INFO: Added file: ' + file)


	def getModuleArguments (self) :
		'''Return a list of arguments for the current module.
			This function will querry the sys.argv[1] parameter
			to figure out what they are. This allows flexibility
			to add new modules without having to define parms in
			the .conf file. They can just be passed with the
			module name.'''

		# Strip out the module name from the standard sys.argv[1]
		# It has to be the first part of the param.
		cmd = sys.argv[1]
		modName = cmd.split()[0]

		# Now strip the module name out and gather up the args
		modArgs = cmd.replace(modName, '').split()

		return modArgs


	def getSystemName (self) :
		'''Return the current system ID.'''

		return self.getSystemSettingsObject()['System']['systemName']


	def getSystemVersion (self) :
		'''Return the current system ID.'''

		return self.getSystemSettingsObject()['System']['systemVersion']


	def getSystemUser (self) :
		'''Return the current system user name.'''

		try :
			return self.getSystemSettingsOverrideObject()['System']['userName']

		except :
			return self.getSystemSettingsObject()['System']['userName']


	def getSystemSourceHomePath (self) :
		'''Return the current system source path.'''

		try :
			return self.getSystemSettingsOverrideObject()['Process']['Paths']['PATH_SOURCE_HOME']

		except :
			return self.getSystemSettingsObject()['Process']['Paths']['PATH_SOURCE_HOME']


	def getSettingsObject (self) :
		'''Return a single settings object for use in normal processes.
			This will pull in the project system and global override
			configuration files and turn them into a combined object
			which will be used on project processes.'''

		projectDefault = self.getProjectDefaultSettingsObject()
		project = self.getProjectSettingsObject()
		sysObj = self.getSystemSettingsObject()
		try :
			override = self.getSystemSettingsOverrideObject()
		except :
			override = ""

		# Now we will merge all the object together to make one master
		# object that will be used for all operations.

		# It is logical, when merging the objects, to think that if
		# there are duplicate keys, the last one in will win. However
		# for whatever reason ConfigObj takes a different approch.
		# In the ConfigObj module it is the first in that wins. In
		# our system we want the object that have the overrides in
		# in it to go in first. That is why the order is the way it
		# is here.

		if project != None :
			try :
				override.merge(sysObj)
				project.merge(override)
			except :
				project.merge(sysObj)

			return project
		else :
			# If no project settings file exists just use the
			# system and override objects
			try :
				override.merge(sysObj)
				projectDefault.merge(override)
			except :
				projectDefault.merge(sysObj)

			return projectDefault


	def getSystemSettingsObject (self) :
		'''Return an object from the ptx-plus.conf which
			contains the system settings.'''

		# There should always be a conf file here
		return ConfigObj(os.environ.get('PTXPLUS_BASE') + "/bin/ptxplus.conf", encoding='utf_8')


	def getProjectSettingsObject (self) :
		'''Return an object which contains the project settings.'''

		if os.path.isfile(os.getcwd() + "/" + self.thisProjectConf()) :
			# Load in the settings from our project
			return ConfigObj(os.getcwd() + "/" + self.thisProjectConf(), encoding='utf_8')


	def getProjectDefaultSettingsObject (self) :
		'''Return a default project object from the system.'''

		# FIXME: This may cause an error because the .conf file
		# may not be found.

		defaultFile = os.environ.get('PTXPLUS_BASE') + "/resources/lib_sysFiles/" + self.thisProjectConf()

		if os.path.isfile(defaultFile) :
			# Load in the settings from our default .conf file
			return ConfigObj(defaultFile, encoding='utf_8')

	def getSystemSettingsOverrideObject (self) :
		'''If it exists, return an object which contains the system override
			settings found in ~/.config/xetex-ptxplus.'''

		home = os.environ.get('HOME')
		overrideFile = home + "/.config/ptxplus/override.conf"

		if os.path.isfile(overrideFile) == True :
			return ConfigObj(overrideFile, encoding='utf_8')


	def makeUserOverrideFile (self) :
		'''Create a user override file but only if it doesn't already exist.'''

		home = os.environ.get('HOME')
		overrideFile = home + "/.config/ptxplus/override.conf"
		if not os.path.isfile(overrideFile) :
			if not os.path.isdir(home + '/.config/ptxplus') :
				os.mkdir(home + '/.config/ptxplus')

			# Make a new empty file if none exists
			object = codecs.open(overrideFile, "w", encoding='utf_8')
			object.close()


	def setSystemUser (self, userName) :
		'''Set the users name in the user config override file.'''

		home = os.environ.get('HOME')
		overrideFile = home + "/.config/ptxplus/override.conf"

		try :
			override = self.getSystemSettingsOverrideObject()
			override['System']['userName'] = userName
			override.write()
		except :
			# If we can't get the object then it probably isn't there, we'll
			# go a head and make one, then write in the information we want.
			if not os.path.isfile(overrideFile) :
				self.makeUserOverrideFile()
				object = codecs.open(overrideFile, "a", encoding='utf_8')
				object.write('# System settings\n')
				object.write('[System]' + '\n\n')
				object.write('# The name of the person using this system.\n')
				object.write('userName = \'' + userName + '\'\n\n')
				object.close()

		# Report what happened
		self.userMessage('INFO: System user name set to: ' + self.getSystemUser())


	def setSystemSourceHome (self, sourceHomePath) :
		'''Set the path to project source files that the system will copy into
			its text folder. This information is stored in the config override file'''

		home = os.environ.get('HOME')
		overrideFile = home + "/.config/ptxplus/override.conf"

		try :
			override = self.getSystemSettingsOverrideObject()
			override['Process']['Paths']['PATH_SOURCE_HOME'] = sourceHomePath
			override.write()
		except :
			# If we can't get the object then it probably isn't there, we'll
			# go a head and make one, set the user name to default then write
			# in the source path information we want.
			if not os.path.isfile(overrideFile) :
				self.makeUserOverrideFile()
				object = codecs.open(overrideFile, "a", encoding='utf_8')
				object.write('# System settings\n')
				object.write('[System]' + '\n\n')
				object.write('# The name of the person using this system.\n')
				object.write('userName = \'Default User\'\n\n')
				object.write('# Process information\n')
				object.write('[Process]' + '\n\n')
				object.write('# System Paths\n')
				object.write('[[Paths]]' + '\n')
				object.write('PATH_SOURCE_HOME = \'' + sourceHomePath + '\'\n\n')
				object.close()
				self.userMessage('INFO: System user name set to: Default User, you may want to change it to the right name with the command: ptxplus set-user\n')
			else :
				object = codecs.open(overrideFile, "a", encoding='utf_8')
				object.write('\n# Process information\n')
				object.write('[Process]' + '\n\n')
				object.write('# System Paths\n')
				object.write('[[Paths]]' + '\n')
				object.write('PATH_SOURCE_HOME = \'' + sourceHomePath + '\'\n\n')
				object.close()

		# Report what happened
		self.userMessage('INFO: System source path set to: ' + self.getSystemSourceHomePath())


	def getScriptureFileID (self, pathPlusFileName, settings_project) :
		'''Return the file ID name from a standard PTX-like file
			name. This assmes a full path in front of the
			file name.'''

		path, file = pathPlusFileName.rsplit("/", 1)
		nameSourceOriginal = settings_project['ProjectText']['SourceText']['NAME_SOURCE_ORIGINAL']
		nameSourceExtention = settings_project['System']['Extensions']['EXT_SOURCE']
		file = file.replace(nameSourceOriginal + "." + nameSourceExtention, "")
		return file


	def getProjectID (self) :
		'''Get the project ID from the .conf file.'''

		return self.getProjectSettingsObject()['Project']['ProjectInformation']['projectID']


	def getProjectType (self) :
		'''Based on the name of the .conf file, return what this
			function thinks the type of this project is.'''

		# This assumes that the name construction is .name.conf
		# we will suck out the "name".
		return self.thisProjectConf().split('.')[1]


	def inProject (self) :
		'''Simple test to see if a .conf file exists.'''

		if os.path.isfile(self.thisProjectConf()) == True :
			return True
		else :
			return False


	def isBackedUp (self) :
		'''Confirm if a backup file exists for a given project.
			This will look in the specified backup dir for
			the backup file related to projectID.'''

		settings = self.getSettingsObject()
		# For the location we use whatever the makefile.conf file has
		# whether it is abs or relative. Note, we use abs in archive_project.py
		backupFilePath = settings['System']['Backup']['backupPath']
		backupFile = backupFilePath + "/Backup.tar.gz"

		if os.path.isfile(backupFile) == True :
			return True
		else :
			return False


	def makeDateStamp (self) :
		# Make a simple date stamp
		n = str(datetime.now())
		nObject = n.split(".")
		rightNow = str(nObject[0])
		rightNow = rightNow.replace("-", "")
		rightNow = rightNow.replace(" ", "")
		rightNow = rightNow.replace(":", "")
		return rightNow + nObject[1]


	def getYMD (self) :
		'''Return a simple YearMonthDay string.'''

		date = str(datetime.today()).split(' ')
		return date[0].replace('-', '')


	def makeUnicodeNumberRange (self, zero) :
		'''Given a standard Unicode codepoint (assumed to be for
			the number "0") in a string this will return the
			range of 0-9. This is useful for regex searches
			in non-Roman texts.'''

		# This will return the actuall human readable numbers in
		# the given language rather than the Unicode hex codes
		return '%s-%s' % (unichr(int(zero, 16)), unichr(int(zero, 16) + 9))


	def makeUID (self) :
		'''Make a simple UID based on time stamp for log entries.
			most processes happen in less than a second, therefore
			we will only use seconds and milliseconds to construct
			the UID.'''

		now = str(datetime.now())
		time = now.split(' ')[1]
		hms, ms = time.split('.')
		s = hms.split(':')[2]
		return s + ms


	def isProjectFolder (self) :
		'''Check to see if the project folder and the .conf file
			exists in the current directory.'''

		path = os.getcwd()
		ok = False
		if os.path.isfile(path + "/" + self.thisProjectConf()) :
			ok = True

		return ok


	def userConfirm (self, msg) :
		'''Ask the user to confirm something.'''

		confirm = False
		answer = raw_input("\nConfirm Action:\n\n" + self.wordWrap(msg, 60) + " (y/n): ")
		if answer.lower() == "y" :

			confirm = True

		elif answer.lower() == "n" :
			self.userMessage("INFO: No is okay too. We can do this another time.")
		else :
			self.userMessage("INFO: I am not sure what you mean by \"" + answer + "\" I am only " \
				"programed for \"y\" or \"n\" I am confused by anything else.")

		return confirm


	def userInput (self, msg) :
		'''Ask the user a question that requires other than y/n input.'''

		return raw_input("\n" + self.wordWrap(msg, 60))


	def userMessage (self, event) :
		'''Output a simple message to the user in the terminal.'''

		# We can make this prettier later.
		print self.wordWrap(event, 60)


	def makefileCommand (self, command) :
		'''Send off a makefile command.'''


		if self.getSettingsObject()['System']['General'].get('debugMode', 'false').lower() == 'true' :
			params = self.getSettingsObject()['System']['MakefileSettings']['makeFileParams']

			# Build the command
			sysCommand = "make " + params + " " + command

			# Send off the command return error code
			return os.system(sysCommand)

		else :

			# Get any special makefile params for debugging
			try :
				params = self.getSettingsObject()['System']['MakefileSettings']['makeFileParams']

				# Build the command
				sysCommand = "make " + params + " " + command

				# Send off the command return error code
				return os.system(sysCommand)

			except :
				self.userMessage('ERROR: Could not run makefile command. The ' + self.thisProjectConf() + ' file may be corrupt.')


	def doCustomProcess (self, processCommand) :
		'''Run a custom command line process on a file. The process string is
			the complete command line with valid paths for all files used.
			Return True if successful.'''

		# Send off the command to the system
		error = os.system(processCommand)

		# Report if the copy actually took place.
		if not error :
			return True
		else :
			return False


	def copyFiles (self, src, dst) :
		'''Copy all the files in a dir to another. It assumes the
			destination dir exists and it will not copy
			recursively.'''

		names = os.listdir(src)
		for name in names:
			srcname = os.path.join(src, name)
			dstname = os.path.join(dst, name)
			if not os.path.isdir(srcname) :
				shutil.copy(srcname, dstname)


	def copyAll (self, src, dst) :
		'''Just like copyFiles but will do folders too it will copy
			them into the destination folder which must exist.'''

		names = os.listdir(src)
		for name in names:
			srcname = os.path.join(src, name)
			dstname = os.path.join(dst, name)
			if not os.path.isdir(srcname) :
				shutil.copy(srcname, dstname)
			else :
				shutil.copytree(srcname, dstname)


	def removeFolder (self, targetDir) :
		'''Hopefully this is a safe way to recursively remove a folder
			and everything in it.'''


		for root, dirs, files in os.walk(targetDir, topdown=False) :
			for name in files :
				os.remove(os.path.join(root, name))
			for name in dirs :
				os.rmdir(os.path.join(root, name))

		os.rmdir(targetDir)


	def cleanUpProject (self, targetDir) :
		'''Clean out all the unecessary project files. Not sure
			if this is in use anywhere. It was made for project
			archiving but the cleanup is now done by excluding
			files we don't want in the archive. This, and the
			functions below may be removed at some point.'''

		self.cleanOutLogFiles(targetDir)
		self.cleanOutBakFiles(targetDir)
		self.cleanOutTexFiles(targetDir)
		self.cleanOutSvnDirs(targetDir)


	def cleanOutLogFiles (self, targetDir) :
		'''Clean out all the .log files in a project.'''

		for root, dirs, files in os.walk(targetDir) :
			for name in files :
				if name.find('.log') > -1 :
					os.remove(os.path.join(root, name))


	def cleanOutBakFiles (self, targetDir) :
		'''Clean out all the .bak and '~' files in a project.'''

		for root, dirs, files in os.walk(targetDir) :
			for name in files :
				if name[-1:] == "~" :
					os.remove(os.path.join(root, name))


	def cleanOutTexFiles (self, targetDir) :
		'''Clean out all the standard TeX files in a project.'''

		#fileList = []
		fileList = '.pdf', '.tex', '.delayed', '.parlocs'
		for root, dirs, files in os.walk(targetDir) :
			for name in files :
				for ext in fileList :
					if name.find(ext) > -1 :
						os.remove(os.path.join(root, name))


	def cleanOutSvnDirs (self, targetDir) :
		'''Clean out any stray .svn folders - just in case. This should be used
			with caution. If you blow away the .svn folders in a live project
			you will have to do alot of back-tracking'''

		for root, dirs, files in os.walk(targetDir) :
			for folder in dirs :
				if folder == ".svn" :
					self.removeFolder(os.path.join(root, folder))


	def wordWrap (self, text, width) :
		'''A word-wrap function that preserves existing line breaks
			and most spaces in the text. Expects that existing line
			breaks are linux style newlines (\n).'''

		def func(line, word) :
			nextword = word.split("\n", 1)[0]
			n = len(line) - line.rfind('\n') - 1 + len(nextword)
			if n >= width:
				sep = "\n"
			else:
				sep = " "
			return '%s%s%s' % (line, sep, word)
		text = text.split(" ")
		while len(text) > 1:
			text[0] = func(text.pop(0), text[0])
		return text[0]


	def walk(self, top, topdown=True, onerror=None) :
		'''Directory tree generator. This was blatantly ripped off
			from os.py. However, the islink function was removed
			to enable walking a tree with links.'''

		from os.path import join, isdir

		try:
			# Note that listdir and error are globals in this module due
			# to earlier import-*.
			names = os.listdir(top)
		except os.error, os.err:
			if onerror is not None:
				onerror(err)
			return

		dirs, nondirs = [], []
		for name in names:
			if isdir(join(top, name)):
				dirs.append(name)
			else:
				nondirs.append(name)

		if topdown:
			yield top, dirs, nondirs
		for name in dirs:
			path = join(top, name)
			for x in self.walk(path, topdown, onerror):
				yield x
		if not topdown:
			yield top, dirs, nondirs


	def prependText (self, text, file) :
		'''Prepend a text string to a file. Return True if successful.
			Log an error and return False if not.'''

		newLines = ""
		# Slurp in all the data in the file
		if os.path.isfile(file) == True :
			orgObject = codecs.open(file, "r", encoding='utf_8')
			for line in orgObject :
				newLines = newLines + line

			orgObject.close()
			newObject = codecs.open(file, "w", encoding='utf_8')
			# Write out the object and stick the additional text to
			# the front of the existing text.
			newObject.write(text + newLines)

			return True
		else:
			return False


	def getSliceOfText (self, text, start, amount) :
		'''For reporting purposes we may want to grab a slice of text to
			send to put in a log event. This will attempt to return a
			a slice of text that equals the amont (number of characters)
			given divided by 2. If it can't do that it will try to get
			as much as it can. The goal is to give the user a resonable
			piece of text so they know what the context is.'''

		text = text.strip()
		if amount > len(text) :
			amount = len(text)

		left = start - (amount / 2)
		right = start + (amount / 2)

		if right > len(text) :
			right = len(text)
			left = right - amount

		if left < 0 :
			left = 0
			right = left + amount
			if right > len(text) :
				right = len(text)

		if text[left:right] == "" :
			return "NO CONTEXT"
		else :
			return text[left:right]

class CSVtoDict(dict):
	'''This class provides a service which will convert a proper CSV file
		that uses the excel dialect and has a header row, into a
		dictionary object. The default record is ID but it can be
		changed to whatever is needed by passing a different value
		for recordkey.'''

	def __init__(self, csv_file_path, recordkey='ID'):
		csvs = csv.DictReader(open(csv_file_path), dialect=csv.excel)
		records = list((row.pop(recordkey),row) for row in csvs)
		return super(CSVtoDict, self).__init__(records)


