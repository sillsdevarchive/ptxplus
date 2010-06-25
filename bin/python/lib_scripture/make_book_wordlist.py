#!/usr/bin/python2.5
# -*- coding: utf_8 -*-
# version: 20090120
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# Generate a word list for the current book being processed.
# This will parse the book and generate a word list and put
# it in the Reports folder.

# History:
# 20090130 - djd - Initial draft
# 20090204 - djd - Completed working first version. However,
#        There is a lot of potential with this process but
#        a lot of work needs to be done such as CSV output
#        on the book report files.
# 20090209 - djd - Completed optimization, works very fast
#        now. We may want to incorporate this in check_book
# 20090323 - djd - With Tim E's help we got the encoding
#        issues ironed out and added true CSV output.
# 20090326 - djd - Moved the process to strip out non-word
#        characters to the encoding manager so it can be
#        shared by other processes.
# 20090401 - djd - Added some better debugging to track
#        possible problems with encoding transformations.
#        Again, Tim E did pretty much all of it
# 20091009 - te - Reordered process and added piping so that
#         a common encoding conversion process could be
#        used rather than having two seperate processes.


#############################################################
######################### Shell Class #######################
#############################################################

import codecs, os, csv
import parse_sfm

# Import supporting local classes
from encoding_manager import *
from tools import *
from collections import defaultdict
tools = Tools()


class MakeBookWordlist (object) :

	def main (self, log_manager) :

		inputFile = log_manager._currentInput
		bookFile = log_manager._currentOutput
		log_manager._currentSubProcess = 'MkBkWrdlst'
		reportPath = log_manager._settings['System']['Paths']['PATH_REPORTS']
		bookReportFile = os.getcwd() + "/" + reportPath + "/" + log_manager._currentTargetID + "-wordlist.csv"
		bookWordlist = {}
		wordlist = []
		pre_wordlist = {}
		raw_str = ''

		# The focus of this script is Scripture text but there maybe times
		# when it is called to work on peripheral matter. At this time we
		# don't want to go there. So, we will filter out peripheral material
		# here by bailing out at this point.
		# Note that the isPeripheralMatter() function is now
		# disabled. Do we really need to do this check anyway?
		# Let's go away and think about it
#        if tools.isPeripheralMatter(inputFile) :
#            return

		# Make our Report folder if it isn't there
		if not os.path.isdir(reportPath) :
			os.mkdir(reportPath)

		# Now we will collect all the words from this book from the text handler
		# and we will apply any encoding changes that are necessary. The process
		# here is more complex than should be but pyTecKit doesn't allow us to
		# do multiple encodings chained together as some projects require. As such
		# we will use a home-spun module to call a shell script that will use the
		# txtconv program to do the encoding conversion externally, then bring it
		# back in to finish the processing. This is done with pipes so it seems
		# very seamless.
		# Bring in any encoding mapings we may need.
		encoder = log_manager._settings['System']['General']['customEncodingProcess']
		if encoder:
			# Process the customEncodingProcess string to set the meta filesnames
			encoder = [arg.replace('[outfile]','/dev/stdout').replace('[infile]',inputFile) for arg in encoder.split()]
			# Run the conversions on all our text
#            log_manager.log("DBUG", 'make_book_wordlist: Preconversion length %d' % len(pre_wordlist))
#            handler._wordlist = pipe_to(encoder, '\n'.join(pre_wordlist)).split('\n')
#            log_manager.log("DBUG", 'make_book_wordlist: Postconversion length %d' % len(filter(bool, handler._wordlist)))

		# Get our book object - Using utf_8_sig because the source
		# might be coming from outside the system and we may need
		# to be able to handle a BOM.
		bookObject = childprocess(encoder).decode('utf_8') if encoder else codecs.open(inputFile, "r", encoding='utf_8_sig').read()

		# Load in the sfm parser
		parser = parse_sfm.Parser()

		# This calls a version of the handler which returns a simple
		# wordlist for us. That will be processed and information harvested
		# from it to be used in our output.
		handler = MakeWordlistHandler(log_manager, wordlist)
		parser.setHandler(handler)
		parser.parse(bookObject)

		pre_wordlist = [s.encode('utf_8') for s in handler._wordlist]

		# Here we create a bookWordlist dict using the defaultdict mod. Then we
		# we add the words we collected from the text handler and do the counting
		# here as well
		bookWordlist = defaultdict(int)
		for word in handler._wordlist:
			bookWordlist[word] += 1


#        # If the lists after removing duplicates and the set before do not match there
#        # may be an encoding problem.  Only generate extended logging info if this is the case
#        num_uniq_pre  = len(set(pre_wordlist))
#        num_uniq_post = len(bookWordlist)
#        if num_uniq_pre != num_uniq_post:
#            log_manager.log("WARN",
#                'possible conversion error: number of unique words do not match: %d -> %d' % (
#                    num_uniq_pre,num_uniq_post))
#
#            # Generate before and after word to word number sets mappings.
#            pre_word_num_map = defaultdict(set)
#            post_word_num_map = defaultdict(set)
#            for n,w in enumerate(pre_wordlist): pre_word_num_map[w].add(n)
#            for n,w in enumerate(handler._wordlist): post_word_num_map[w].add(n)
#
#            larger  = (pre_wordlist,      set(map(tuple,pre_word_num_map.values())),  'source')
#            smaller = (handler._wordlist, set(map(tuple,post_word_num_map.values())), 'target')
#            # we always need to take the smaller set from the larger so there are more words
#            # /after/ the conversion swap them around
#            if num_uniq_pre < num_uniq_post: larger, smaller = smaller,larger
#            for ids in larger[1].difference(smaller[1]):
#                for i in ids:
#                    log_manager.log("DBUG",
#                        '%s text word no. %d has ambiguous mapping in %s: codepoint sequences (source -> target): %s -> %s' % (
#                            larger[2], i, smaller[2],
#                            unicode_sequence(pre_wordlist[i].decode('utf_8')),
#                            unicode_sequence(handler._wordlist[i].decode('utf_8'))))

		# Write out the new csv book word count file
		# More info on writing to csv is here:
		#    http://docs.python.org/library/csv.html#writer-objects
		cvsBookFile = csv.writer(open(bookReportFile, "wb"), dialect=csv.excel)
		cvsBookFile.writerows(bookWordlist.items())

		# Report what happened
		log_manager.log("INFO", "Process complete. Total words found = " + str(len(handler._wordlist)) + " / Unique words = " + str(len(bookWordlist)))


def unicode_sequence(s):
	'''This creates a human-readable sequence of unicode code points'''

	return '<' + ' '.join("%04x" % ord(u) for u in s) + '>'


class MakeWordlistHandler (parse_sfm.Handler) :
	'''This class replaces the Handler class in the parse_sfm module.'''

	def __init__(self, log_manager, wordlist) :

		self.log_manager = log_manager
		self._wordlist = wordlist
		self._book = ""
		self._quotemap = {}
		#self._nonWordCharsMap = {}
		self.encoding_manager = EncodingManager(log_manager._settings)

		cList = ""
		# This is only for report what we will be using in this
		# process for non-word characters
		for c in self.encoding_manager._nonWordCharsMap :
			cList = cList + unichr(c) + "|"

		self.log_manager.log("INFO", "The process will exclude these characters from all words: [" + cList.rstrip('|') + "]")


	def start (self, tag, num, info, prefix) :
		'''This tells us when a tag starts. We will use this information to set location
			and trigger events.'''

		# Track the location
		self.log_manager.setLocation(self._book, tag, num)

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


		# Whatever happened, return the results now
		if info.isChar and not info.isNonPub :
			words = text.split()
			for word in words :
				word = word.strip()
				# Add it to the dictionary if it is a real word
				if self.isWord(word) :
					# Strip out any non-word chars
					word = self.encoding_manager.stripNonWordCharsFromWord(word)
					# Whatever is left we will add to our all words dictionary
					if word :
						self._wordlist.append(word)

		# This may not be needed
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


	def isWord (self, word) :
		'''Check to see if this is a word not a reference or number.'''

		if not self.encoding_manager.isReferenceNumber(word) and not self.encoding_manager.isNumber(word) :
			return True


# This starts the whole process going
def doIt (log_manager) :
	thisModule = MakeBookWordlist()
	return thisModule.main(log_manager)

