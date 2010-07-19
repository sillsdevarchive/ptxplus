#!/usr/bin/python2
# -*- coding: utf_8 -*-
# version: 20081124
# By Dennis Drescher (dennis_drescher at sil.org)
#	(The core was ghost-written by Martin Hosken)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with other versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This is a PTX style file (.sty) parser. It is designed to
# parse a .sty file and return an object which contains all
# sfm style information found in the file. This is typically
# used to parse the PTX usfm.sty file.

# History:
# 20090114 - djd - Initial draft


#############################################################
#################### Initialize The Process #################
#############################################################
# Firstly, import all the standard Python modules we need for
# this process

import re

# This is what a marker looks like in regex
markerDef = re.compile(r'(?s)\\([^\\\s]+)(\s*[^\\]*)')

def init_ptx () :
	'''Initialize the module with global defaults for parsing Paratext usfm files.'''

	ptxInfo = {
		'Marker'			: ['isMarker'],
		'Endmarker'			: ['isEndMarker'],
		'Name'				: ['isDescription'],
		'Description'		: ['isDescription'],
		'StyleType'			: ['isDescription', 'isType'],
		'TextProperties'	: ['isDescription'],
		'TextType'			: ['isDescription', 'isType'],
		'Rank'				: ['isDescription'],
		'OccursUnder'		: ['isDescription'],
		'Bold'				: ['isFormat', 'forFont'],
		'Italic'			: ['isFormat', 'forFont'],
		'Regular'			: ['isFormat', 'forFont'],
		'FontSize'			: ['isFormat', 'forFont'],
		'Color'				: ['isFormat', 'forFont'],
		'SpaceBefore'		: ['isFormat', 'forPara'],
		'SpaceAfter'		: ['isFormat', 'forPara'],
		'Justification'		: ['isFormat', 'forPara'],
		'Superscript'		: ['isFormat', 'forPara'],
		'FirstLineIndent'	: ['isFormat', 'forPara'],
		'LeftMargin'		: ['isFormat', 'forPara'],
		'RightMargin'		: ['isFormat', 'forPara']
	}

	# Add the above para attributes to the SFM tuple list
	for (s, a) in ptxInfo.iteritems() :
		res[s] = parse.STY()

	return res



class STY (object) :
	'''This defines to the parser what a style marker can contain.'''

	def __init__ (self) :

		self.isMarker			= False
		self.isEndMarker		= False
		self.isDescription		= False
		self.isType				= False
		self.isFormat			= False
		self.forFont			= False
		self.forPara			= False

	def __repr__ (self) :
		res = "STY( "
		for s in ('isMarker', 'isEndMarker', 'isDescription', 'isType', \
			'isFormat', 'forFont', 'forPara') :
			if self.__getattribute__(s) : res += s + " "
		res += ")"
		STY = res


class Parser (object) :
	'''This is the main class which parses an STY object and returns an object.'''


	# This is a class-wide object
	# Pull in sty definitions
	styles = init_ptx()


	def __init__ (self) :
		'''Initialize the class'''

		self.stack = list()


	def getSTYDefinitions (self, filename) :
		'''Pull in the style definitions of all possible USFM markers covered
			in the .sty file.'''

		Parser.styles = {}


	def parse (self, string) :
		'''Intitial string parse where we are only looking for a marker. Once found
			it is passed on to the marker() function.'''

		for match in (markerDef.finditer(string)) :
			self._prefix = string[match.start(1)-2] if match.start(1) > 1 else ''
			self.marker(match.group(1), match.group(2))


	def marker (self, tag, text) :
		'''The core function of this class which identifes all style markers found.
			It returns an object called res which contains style data.'''

		res = ''

		if Parser.styles.has_key(tag) and Parser.styles[tag].isEmpty :
			res = self.handler.start(tag, '', Parser.styles[tag])
			r = self.handler.end(tag, tag, Parser.styles[tag])
			res = self.merge(res, r)
			r = self.handler.text(text, tag, Parser.styles[tag])
			res = self.merge(res, r)
		else :
			if len(self.stack) :
				ind = len(self.stack) - 1
				if Parser.styles.has_key(tag) and Parser.styles[tag].isChar :
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
				info = (tag, Parser.styles[tag] if Parser.styles.has_key(tag) else STY(()))
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
