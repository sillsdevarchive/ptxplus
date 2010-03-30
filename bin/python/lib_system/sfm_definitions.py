#!/usr/bin/python
# -*- coding: utf-8 -*-
# version: 20081124
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with other versions.

#############################################################
################ Description/Documentation ##################
#############################################################

# This is the an SFM definition module. It provides guidence on
# how the parse_sfm.py module will act as it parses SFM text.
# Default types of SFM text should be defined here


#from parse_sfm import *
import parse_sfm


def init_usfm () :
	'''Initialize the module with global defaults for USFM standard.'''

	# Instantiate Parser classes
	parse = parse_sfm

	# Create the new dictionary object we will return
	res = dict()

	# Create a temp dictionary of attributes for common USFM markers
	sfmInfo = {
		'id'		: ['isNonV', 'isNonPub'],
		'ide'		: ['isNonV', 'isNonPub'],
		'rem'		: ['isNonV', 'isNonPub'],
		'c'		: ['isNum'],
		'v'		: ['isNum', 'isChar'],
		'va'		: ['isEnd', 'isChar', 'isInline'],
		'vp'		: ['isEnd', 'isChar', 'isInline'],
		'qs'		: ['isEnd', 'isChar', 'isInline'],
		'qac'		: ['isEnd', 'isChar', 'isInline'],
		'f'		: ['isEnd', 'isChar', 'isNote', 'isNonPub', 'isInline'],
		'fe'		: ['isEnd', 'isChar', 'isNote', 'isInline'],
		'fr'		: ['isChar', 'isNote', 'isInline', 'isRef'],
		'fk'		: ['isChar', 'isNote', 'isInline'],
		'ft'		: ['isChar', 'isNote', 'isInline'],
		'fq'		: ['isChar', 'isNote', 'isInline'],
		'fqa'		: ['isChar', 'isNote', 'isInline'],
		'fl'		: ['isChar', 'isNote', 'isInline'],
		'fp'		: ['isChar', 'isNote', 'isInline'],
		'fv'		: ['isChar', 'isNote', 'isInline'],
		'fdc'		: ['isEnd', 'isChar', 'isNote', 'isInline'],
		'fm'		: ['isEnd', 'isChar', 'isNote', 'isInline'],
		'x'		: ['isEnd', 'isChar', 'isNote', 'isNonPub', 'isInline'],
		'xo'		: ['isChar', 'isNote', 'isInline', 'isRef'],
		'xt'		: ['isChar', 'isNote', 'isInline'],
		'xk'		: ['isChar', 'isNote', 'isInline'],
		'xq'		: ['isChar', 'isNote', 'isInline'],
		'xdc'		: ['isEnd', 'isChar', 'isNote', 'isInline'],
		'qt'		: ['isEnd', 'isChar', 'isInline'],
		'nd'		: ['isEnd', 'isChar', 'isInline'],
		'tl'		: ['isEnd', 'isChar', 'isInline'],
		'dc'		: ['isEnd', 'isChar', 'isInline'],
		'bk'		: ['isEnd', 'isChar', 'isInline'],
		'sig'		: ['isEnd', 'isChar', 'isInline', 'isFormat'],
		'pn'		: ['isEnd', 'isChar', 'isInline', 'isFormat'],
		'k'		: ['isEnd', 'isChar', 'isInline', 'isFormat'],
		'sls'		: ['isEnd', 'isChar', 'isInline'],
		'add'		: ['isEnd', 'isChar', 'isInline'],
		'ord'		: ['isEnd', 'isChar', 'isInline'],
		'no'		: ['isEnd', 'isChar', 'isInline'],
		'it'		: ['isEnd', 'isChar', 'isInline', 'isFormat'],
		'bd'		: ['isEnd', 'isChar', 'isInline', 'isFormat'],
		'bdit'		: ['isEnd', 'isChar', 'isInline', 'isFormat'],
		'em'		: ['isEnd', 'isChar', 'isInline'],
		'sc'		: ['isEnd', 'isChar', 'isInline'],
		'pb'		: ['isEmpty'],
		'pro'		: ['isEnd', 'isNonPub', 'isChar', 'isInline'],
		'w'		: ['isEnd', 'isChar', 'isInline'],
		'wg'		: ['isEnd', 'isChar', 'isInline'],
		'wh'		: ['isEnd', 'isChar', 'isInline'],
		'wj'		: ['isEnd', 'isChar', 'isInline'],
		'ndx'		: ['isEnd', 'isChar', 'isInline'],
		'periph'	: ['isNonPub', 'isNonV'],
		'efm'		: ['isEnd', 'isChar', 'isNonV', 'isNote', 'isInline'],
		'ef'		: ['isEnd', 'isNote', 'isNonPub'],
		'fig'		: ['isEnd', 'isInline', 'isNonV']
	}

	# Add the above attributes to the SFM tuple list
	for (s, a) in sfmInfo.iteritems() :
		res[s] = parse.SFM(a)

	# Create temp dict with normal paragraph elements and attributes
	# Note: we may need to split some of these out to their own
	# section at some point
	paraInfo = {
		'p'		: ['isPara', 'isChar'],
		'm'		: ['isPara', 'isChar'],
		'pmo'		: ['isPara', 'isChar'],
		'pm'		: ['isPara', 'isChar'],
		'pmc'		: ['isPara', 'isChar'],
		'pmr'		: ['isPara', 'isChar'],
		'mi'		: ['isPara', 'isChar'],
		'nb'		: ['isPara', 'isChar'],
		'cls'		: ['isPara', 'isChar'],
		'pc'		: ['isPara', 'isChar'],
		'pr'		: ['isPara', 'isChar'],
		'b'		: ['isPara', 'isChar']
	}

	# Add the above normal para attributes to the SFM tuple list
	for (s, a) in paraInfo.iteritems() :
		res[s] = parse.SFM(a)

	# Create a temp dict with introduction elements and attributes
	# This will not contain numbered elements
	introInfo = {
		'ip'			: ['isPara', 'isChar', 'isIntro'],
		'ipi'			: ['isPara', 'isChar', 'isIntro'],
		'im'			: ['isPara', 'isChar', 'isIntro'],
		'imi'			: ['isPara', 'isChar', 'isIntro'],
		'ipq'			: ['isPara', 'isChar', 'isIntro'],
		'imq'			: ['isPara', 'isChar', 'isIntro'],
		'ipr'			: ['isPara', 'isChar', 'isIntro'],
		'ib'			: ['isPara', 'isChar', 'isIntro'],
		'iot'			: ['isPara', 'isChar', 'isIntro'],
		'iex'			: ['isPara', 'isChar', 'isIntro'],
		'imte'			: ['isPara', 'isChar', 'isIntro'],
		'ie'			: ['isPara', 'isChar', 'isIntro'],
		'ior'			: ['isEnd', 'isChar', 'isInline', 'isIntro']
	}

	# Attributes for para markers with levels, including poetry
	# (but we may need to separate this out)
	for k in ('pi', 'li', 'ili', 'ph', 'q', 'iq') :
		res[k] = parse.SFM(['isPara', 'isChar'])
		for n in range(1, 4) :
			res[k + str(n)] = parse.SFM(['isPara', 'isChar'])

	# Attributes for heading markers with levels. This can be
	# used for all kinds of title markers that use level numbers
	# since the range is always 1-4
	for k in ('h', 'mt', 'mte', 'ms', 's', 'imt', 'is', 'io') :
		res[k] = parse.SFM(['isTitle', 'isChar'])
		for n in range(1, 4) :
			res[k + str(n)] = parse.SFM(['isTitle', 'isChar'])

	# Attributes for reference markers
	for k in ('mr', 'sr', 'r', 'rq', 'd', 'sp') :
		res[k] = parse.SFM(['isTitle', 'isChar'])

	# Attributes for table markers
	for k in ('th', 'tc', 'thr', 'tcr') :
		for n in range(1, 4) :
			res[k + str(n)] = parse.SFM(['isEnd', 'isChar'])

	# Supplemental, "private use" non-USFM markup that could be used
	for k in ('ct') :
		for n in range(1, 4) :
			res[k + str(n)] = parse.SFM(['isPara', 'isTitle', 'isChar'])

	res['spacer'] = parse.SFM(['isFormat'])
	res['tah'] = parse.SFM(['isEnd', 'isChar', 'isInline', 'isFormat'])
	res['tar'] = parse.SFM(['isEnd', 'isChar', 'isInline', 'isFormat'])
	res['z_pn'] = parse.SFM(['isEnd', 'isChar', 'isInline', 'isFormat'])
	res['z_pg'] = parse.SFM(['isEnd', 'isChar', 'isInline', 'isFormat'])

	return res


def init_mdf () :
	'''Initialize the module with global defaults for MDF standard.'''

	# Instantiate Parser classes
	parse = parse_sfm

	# Create the new dictionary object we will return
	res = dict()

	# Create a temp dictionary of attributes for common MDF markers
	sfmInfo = {
		'1d'		: [''],
		'1e'		: [''],
		'1i'		: [''],
		'1p'		: [''],
		'1s'		: [''],
		'2d'		: [''],
		'2p'		: [''],
		'2s'		: [''],
		'3d'		: [''],
		'3p'		: [''],
		'3s'		: [''],
		'4d'		: [''],
		'4p'		: [''],
		'4s'		: [''],
		'an'		: [''],
		'bb'		: [''],
		'bw'		: [''],
		'ce'		: [''],
		'cf'		: [''],
		'cn'		: [''],
		'cr'		: [''],
		'de'		: [''],
		'dn'		: [''],
		'dr'		: [''],
		'dt'		: [''],
		'dv'		: [''],
		'ec'		: [''],
		'ee'		: [''],
		'eg'		: [''],
		'en'		: [''],
		'er'		: [''],
		'es'		: [''],
		'et'		: [''],
		'ev'		: [''],
		'ge'		: [''],
		'gn'		: [''],
		'gr'		: [''],
		'gv'		: [''],
		'hm'		: [''],
		'is'		: [''],
		'lc'		: [''],
		'le'		: [''],
		'lf'		: [''],
		'ln'		: [''],
		'lr'		: [''],
		'lt'		: [''],
		'lv'		: [''],
		'lx'		: [''],
		'mn'		: [''],
		'mr'		: [''],
		'na'		: [''],
		'nd'		: [''],
		'ng'		: [''],
		'np'		: [''],
		'nq'		: [''],
		'ns'		: [''],
		'nt'		: [''],
		'oe'		: [''],
		'on'		: [''],
		'or'		: [''],
		'ov'		: [''],
		'pc'		: [''],
		'pd'		: [''],
		'pde'		: [''],
		'pdl'		: [''],
		'pdn'		: [''],
		'pdr'		: [''],
		'pdv'		: [''],
		'ph'		: [''],
		'pl'		: [''],
		'pn'		: [''],
		'ps'		: [''],
		'rd'		: [''],
		're'		: [''],
		'rf'		: [''],
		'rn'		: [''],
		'rr'		: [''],
		'sc'		: [''],
		'sd'		: [''],
		'se'		: [''],
		'sg'		: [''],
		'sn'		: [''],
		'so'		: [''],
		'st'		: [''],
		'sy'		: [''],
		'tb'		: [''],
		'th'		: [''],
		'ue'		: [''],
		'un'		: [''],
		'ur'		: [''],
		'uv'		: [''],
		'va'		: [''],
		've'		: [''],
		'vn'		: [''],
		'vr'		: [''],
		'we'		: [''],
		'wn'		: [''],
		'wr'		: [''],
		'xe'		: [''],
		'xn'		: [''],
		'xr'		: [''],
		'xv'		: ['']
	}

	# Add the above para attributes to the SFM tuple list
	for (s, a) in sfmInfo.iteritems() :
		res[s] = parse.SFM()

	return res
