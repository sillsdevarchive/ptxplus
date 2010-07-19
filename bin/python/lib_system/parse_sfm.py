#!/usr/bin/python2
# -*- coding: utf_8 -*-
# version: 20081124
# By Dennis Drescher (dennis_drescher at sil.org)
#    (The core was ghost-written by Martin Hosken)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with other versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This is an SFM parser (scanner) based on Martin Hosken's
# USFM.pm module It is designed to parse SFM text and return
# information based on the context of the markers found.

# Basic usage:

# import parse_sfm
# class MyClass (object) :
#    def myFunction (self, ) :
#        bookObject = "".join(codecs.open(inputFile, "r", encoding='utf_8_sig'))
#        parser = SFM.Parser()
#        parser.transduce(bookObject)

# To specify a custom handler, in your application you would use:

# Parser.setHandler(self.myHandler)


# History:
# 20081124 - mjph - Initial draft
# 20081125 - djd - Added basic documentation.
# 20081210 - djd - Seperated SFM definitions from the module
#        to allow for parsing other kinds of SFM models
#        Also changed the name to parse_sfm.py as the
#        module is more generalized now
# 20090214 - djd - Added error handling for missing tags


#############################################################
#################### Initialize The Process #################
#############################################################
# Firstly, import all the standard Python modules we need for
# this process

import re
from sfm_definitions import *

# Set global vars and objects here
# This is what a marker looks like in regex
markerDef = re.compile(r'(?s)\\([^\\\s]+)(\s*[^\\]*)')


class SFM (object) :
	'''This defines to the parser what an SFM is.'''

	def __init__ (self, settings = None) :

		self.isChar        = False
		self.isEmpty    = False
		self.isEnd        = False
		self.isFormat    = False
		self.isInline    = False
		self.isNonPub    = False
		self.isNonV        = False
		self.isNote        = False
		self.isNum        = False
		self.isPara        = False
		self.isRef        = False
		self.isTitle    = False
		self.isInfo        = False

		if settings :
			for s in settings :
				self.__setattr__(s, True)

	def __repr__ (self) :
		res = "SFM( "
		for s in ('isChar', 'isEmpty', 'isEnd', 'isFormat', 'isInline', \
			'isNonPub', 'isNonV', 'isNote', 'isNum', 'isPara', 'isRef', \
			'isTitle', 'isInfo') :
			if self.__getattribute__(s) : res += s + " "
		res += ")"
		return res


class Parser (object) :
	'''This is the main class which parses an SFM object and returns, when called
		various bits of information about the text contained in the object.'''

# This isn't right. It needs to be some simple default that is overridden or moved someplace else
	# This is a class-wide object
	# Pull in sfm definitions
	sfms = init_usfm()
#################################################################################################

	def __init__ (self) :
		'''Initialize the class'''

		# Set the default handler
		self.handler = Handler()
		self.stack = list()
		self._prefix = ""

	def __repr__ (self):
		return 'Parser: handler=%s stack=%s _prefix="%s"' % (self.handler, self.stack, self._prefix)

	def getSFMDefinitions (self, filename, replace = 0) :
		'''Pull in the definitions of the possible USFM markers we might find.
			In this first version we will just bring in the default definitions
			Later we will add the ability to read in USFM PTX style files which
			will override the default setting.'''

		if replace == 1 :
			Parser.sfms = {}


	def setHandler (self, handler) :
		'''Overrides the default handler set during init. with the calling
			applications own handler.'''

		self.handler = handler


	def parse (self, string) :
		'''Intitial string parse where we are only looking for a marker. Once found
			it is passed on to the marker() function.'''

		for match in (markerDef.finditer(string)) :
			self._prefix = string[match.start(1)-2] if match.start(1) > 1 else ''
			self.marker(match.group(1), match.group(2))


	def transduce (self, string) :
		'''Does a global replacement on the incoming string and
			returns the new text. Useful for encoding conversions.'''

		def replaceMe (newObj) :
			self._prefix = newObj.string[newObj.start(1)-2] if newObj.start(1) > 1 else ''
			res = self.marker(newObj.group(1), newObj.group(2))
			return str(res)
		res = markerDef.sub(replaceMe, string)
		res += self.marker('', '')
		return res


	def cleanCopy (self, string) :
		'''Using parsed text, output a clean copy of the entire file.'''

		return


	def marker (self, tag, text) :
		'''The core function of this class which identifes all markers found. It returns
			an object called res which contains data that is determined by the handler
			class. This module contains a default handler but it can be substituted by
			the calling application.'''
		res = ''
#        print 'marker: "%s" "%s"' % (tag, text)
		# Here we strip off the "*"
		x = tag.find('*')
		if x != -1 :
			text = tag[x+1:] + text
			tag = tag[:x]

		if x != -1 :
			temp = []
			while self.stack :
				info = self.stack.pop()
				if info[0] == tag :
					while len(temp) :
						t = temp.pop()
						if not t[1] :
							t[1] = SFM(('isEnd', 'isChar'))
						r = self.handler.end(t[0], tag +"*", t[1])
						res = self.merge(res, r)
					if not info[1] :
						info[1] = SFM(('isEnd', 'isChar'))
					r = self.handler.end(info[0], tag + "*", info[1])
					res = self.merge(res, r)
					if self.stack :
						r = self.handler.text(text, self.stack[-1][0], self.stack[-1][1])
						res = self.merge(res, r)
					break
				else :
					temp.insert(0, info)
			if temp :
				self.handler.error(tag + "*", text, "No open tag for closing tag")
				# error recovery code, treat as just a tag of unknown purpose
				self.stack.extend(temp)
				if Parser.sfms.has_key(tag) :
					info = (tag, Parser.sfms[tag])
				else :
					info = (tag, SFM(()))
				r = self.start(tag + "*", text, info)
				res = self.merge(res, r)
				self.stack.append(info)
				r = self.handler.text(text, tag + "*", info[1])
				res = self.merge(res, r)

		elif Parser.sfms.has_key(tag) and Parser.sfms[tag].isEmpty :
			# Just in case we have a bad tag here
			try :
				res = self.handler.start(tag, '', Parser.sfms[tag])
			except :
				self.handler.error(tag, text, "This tag is not registered with the system.")

			r = self.handler.end(tag, tag, Parser.sfms[tag])
			res = self.merge(res, r)
			r = self.handler.text(text, tag, Parser.sfms[tag])
			res = self.merge(res, r)
		else :
			if len(self.stack) :
				ind = len(self.stack) - 1
				if Parser.sfms.has_key(tag) and Parser.sfms[tag].isChar :
					while ind >= 0 and self.stack[ind][0] != tag :
						ind -= 1
					if ind < 0 : ind = len(self.stack)
				else :
					while ind >= 0 and self.stack[ind][0] != tag :
						ind -= 1
					if ind < 0 : ind = 0
				while len(self.stack) > ind :
					info = self.stack.pop()
					r = self.handler.end(info[0], tag, info[1])
					res = self.merge(res, r)
			if tag :
				info = (tag, Parser.sfms[tag] if Parser.sfms.has_key(tag) else SFM(()))
				r = self.start(tag, text, info)
				res = self.merge(res, r)
				self.stack.append(info)
		return res


	def merge (self, old, new) :
		if not new :
			return old
		elif old :
			return old + new
		else :
			return new

		res = (f[0] + f[1] for f in zip(old, new))
		res.extend(old[len(new)+1:]) if len(old) > len(new) else new[len(old)+1:]
		return res


	def start (self, tag, text, info) :
		word = re.compile(r'(?s)^\s*(\S+)')
#        print tag, text
		if info[1].isNum :
			m = word.search(text)
			firstword = m.group(1)
			text = text[:m.start()] + text[m.end():]
		else :
			firstword = ''
		res = self.handler.start(tag, firstword, info[1], self._prefix)
		r = self.handler.text(text, tag, info[1])
		res = self.merge(res, r)
		return res


class Handler (object) :
	'''This is the API of this module. This is called by the marker() class and enables
		it to know what to return to the calling application. Custom versions of this
		handler can be put in other applications and substitute this one. At a minimum
		the custom handler must have three functions, they are, start(), text(), and
		end().'''

	def start (self, tag, num, info) :
		if num != '' :
			if (tag == 'c') : self.chapter = num
			elif (tag == 'v') : self.verse = num
			return "\\" + tag + " " + num
		else :
			return "\\" + tag

	def text (self, text, tag, info) :
		if (tag == 'id') : self.book = text.split(None, 0)[0]
		return text

	def end (self, tag, ctag, info) :
		if tag + "*" == ctag :
			return "\\" + ctag

	def error (self, tag, text, msg) :
		pass
