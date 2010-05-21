#!/usr/bin/python2.5
# -*- coding: utf-8 -*-

# This is a simple differential testing script for simple
# word lists. It assumes the list has one word per line.
# Parts of this will hopefully be added to the tools.py
# utility script in ptxplus.

# Import necessary modules
import codecs, sys, operator
from itertools import *

# Information on how sets work are at:
#	http://docs.python.org/library/stdtypes.html#set-types-set-frozenset
# This simple function basically uses the intersection (&)
# and difference (-) calls to create the output. These are
# called like mathematical equations.
def wordlist_diff(prev, current):
	strip = operator.methodcaller('strip')
	prev = set(imap(strip, prev))
	curr = set(imap(strip, current))
	return (prev-curr, prev & curr, curr-prev)

# Create output file names
com = 'common.txt'
dif = 'dif.txt'

# Call the core function to create the output
removed, common, added = wordlist_diff(codecs.open(sys.argv[1], "r", encoding='utf_8_sig'),
				codecs.open(sys.argv[2], "r", encoding='utf_8_sig'))


# Write out the differential results to cwd (change this as
# needed for the job) To write to screen do:
#	outDif = codecs.getwriter('utf-8')(sys.stdout)
outDif = codecs.open(dif, 'w', encoding='utf_8_sig')
outDif.write(' '.join(dif) + '\n')
outDif.write('---- ' + sys.argv[1] + '\n')
outDif.write('++++ ' + sys.argv[2] + '\n')
outDif.writelines(sorted(("- " + w + '\n') for w in removed))
outDif.writelines(sorted(("+ " + w + '\n') for w in added))
outDif.close()

# Write out the common words list
outCom = codecs.open(com, 'w', encoding='utf_8_sig')
outCom.write(' '.join(com) + '\n')
outCom.writelines(sorted((w + '\n') for w in common))
outCom.close()
