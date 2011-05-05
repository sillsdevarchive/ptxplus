#!/usr/bin/perl
# MergePages.pl
# Sheldon Kehler -- March 2006

# Script to merge pages from pdf files in order to produce combined pdf for printer.
# This perl script no longer works without producing 1000s of "Missing or invalid MediaBox" errors in the console log. It
# calls an old reuse.pm file, both versions of which are out-of-date and cause problems.  16 Jul 2009 jw

# ToDo:

# 1) keep track of number of pages printed and force even/odd boundaries

# 2) maybe eventually update page numbers as output


use PDF::Reuse;
use strict;


my ($pdf, $i, $numPages, $filename);


prFile('Joan.merged.pdf');
  addfile('PATSURResetTitlePages.pdf');
# addfile('HebTrans.Intro.pdf');
# addfile('Jon.intro.pdf');

 interleave('PATSURResetSize.pdf', 'MAT.free.pdf');
# interleave('PATSURResetSize.pdf', 'PATDI.free.pdf');

prEnd();

print "Done\n";
exit;


sub interleave {

  my ($fn1, $fn2) = @_;

  my $numPages = max(getPDFNbrPages($fn1), getPDFNbrPages($fn2));

  foreach my $i (1..$numPages) {

	prDoc( { file  => $fn1,
			first => $i,
			last  => $i });

	prDoc( { file  => $fn2,
			first => $i,
			last  => $i });
  }
}


sub addfile {

  my $fn = shift;
  my $nbrPages = getPDFNbrPages($fn);

  prDoc( { file  => $fn,
		  first => 1,
		  last  => $nbrPages });
}


sub getPDFNbrPages {

  my $fn = shift;
  my ($nbrPages, $inTypePages) = (0, 0);

  open FL, "$fn" or die "Can't open file $fn\n";
  binmode FL;

  while (<FL>) {
	if (/\/Type\s*\/Pages/) {

	  $inTypePages = 1;
	}

	if ($inTypePages && /\Count (\d*)/) {
	  $nbrPages = $1;
	}

	if ($inTypePages && /endobj/) {
	  $inTypePages = 0;
	}
  }

  close FL;

  return $nbrPages;
}


sub max {

  my ($f, $s) = @_;
  return $f > $s ? $f : $s;
}
