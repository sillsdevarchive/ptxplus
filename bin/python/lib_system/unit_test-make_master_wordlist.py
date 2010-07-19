#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20090120
# By Dennis Drescher (dennis_drescher at sil.org)

# This script has been tested on Python 2.5.1 (Ubuntu)
# it may not work right with earlier versions.

# This is a unit test written by Tim Eves used to test the output from
# a master wordlist file against the individual files that created it.
# To use it copy this file into the Reports directory and use:
#        unit_test-make_master_wordlist wordlist-master.csv *-wordlist.csv


from __future__ import with_statement
from collections import defaultdict
import csv

def merge_items(items):
	r = defaultdict(int)
	for item in items:
		for k,v in item: r[k] += int(v)
	return dict(r)

if __name__ == '__main__':
	import sys
	master = sys.argv[1]
	books  = sys.argv[2:]

	synthetic = merge_items([csv.reader(open(bk,'rb')) for bk in books])
	actual    = dict((k,int(v)) for k,v in csv.reader(open(master,'rb')))

	if synthetic == actual:
		print 'match'
	else:
		print 'mismatched'
		print('total books entries  =', len(synthetic))
		print('total master entires =', len(actual))
		mismatched = {}
		only_master = []
		for word,count in actual.items():
			s_count = synthetic.get(word)
			if s_count:
				if s_count != count:
					mismatched[word] = (count,s_count)
				del synthetic[word]
			else:
				only_master.append(word)
		print('words only in master list:')
		for word in only_master:  print '\t',word
		print('\nwords only in books:')
		for word in synthetic:  print '\t',word
		print('\nwords with mismatched counts (master, books):' )
		for word,(mc,sc) in mismatched.items(): print '\t',word,'\t',mc,'!=',sc

