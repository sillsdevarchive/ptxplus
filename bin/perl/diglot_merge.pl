#!/usr/bin/perl -w
use strict;
my $logging=0;
my (@leftdata, @rightdata);
my (@chunkline,@chunkdata,@pos);
my $maxactive=4;
my $savelimit=0;
my %active;
my ($start,$stop)=(undef,undef);
my @sides=('left','right');
my @chunk=("","");
my @position=('::000::000:::::::','::000::000:::::::');
my @inrange;
my @heading;
my @first_inrange; # Shortcut to the start of interesing data

# Could do this in less memory, but it's way easier like this
sub readfile {
	my ($name)=@_;
	my @result;
	logit(undef,"Opening $name");
	open(FILE,"<",$name) || die($name.": $!");
	local $/;
	@result=map {s/\r\n/\n/;$_} map {split(/(\\\S+)/)} (<FILE>);
	close(FILE);
	logit(undef,"Closed $name");
	return @result;
}

sub logit { # Gerneral purpose logging routine
	my ($side)=shift(@_);
	if ($logging) {
		if (defined($side)) {
			print LOG (join(" ",$sides[$side],$position[$side],@_)."\n");
		} else {

			print LOG (join(" ",@_)."\n");
		}
	}
}

sub ref_to_pos { # Create a unique position identifier from a reference
	my ($ref)=@_;
	my @range;
	foreach my $idx (0..$maxactive) {
		$range[$idx]='';
	}
	if ($ref =~ /(\d+):(\d+)/) {
		$range[1]=sprintf("%03d",$1);
		$range[2]=sprintf("%03d",$2);
		$ref=join('::',@range);
	} else {
		printf STDERR ("Could not decode reference '%s'\n",$ref);
		exit(2);
	}
	return($ref);
}
my %inrange_cache;

sub inrange {
	my ($ref)=@_;
	if (!defined($inrange_cache{$ref})) {
		$inrange_cache{$ref}=_inrange($ref);
	}
	#logit(undef,$ref,$inrange_cache{$ref});
	return($inrange_cache{$ref});
}
sub _inrange { # Because we may only want a selection of the input files.
	my ($ref)=@_;
	#print ("Inrange: $ref\n");
	if (!defined($start)) {
		return 1;
	}
	if ($ref ge $start) {
		if (!defined($stop) or ($ref le $stop)) {
			return 1;
		}
	}
	my (@startpos,@curpos);
	@startpos=split('::',$start);
	@curpos=split('::',$ref);
	if ($startpos[1] eq $curpos[1] and $curpos[2] eq '000' ) {
		return 1;
	}
	if ($curpos[1] eq '000' and $curpos[2] eq '000') {
		return 1;
	}
	#logit(undef,$ref,"Out of range");
	return 0;
}

my $notext;
sub do_output {
	my ($pos,$chunkref)=@_;
	if ($$chunkref[1]=~/^(?:\\p|\n|\s)+$/) {
		$$chunkref[1]="";
	}
	if ($$chunkref[0]=~/^(?:\\p|\n|\s)+$/) {
		$$chunkref[0]="";
	}
	if ($$chunkref[0] eq "" and $$chunkref[1] eq "") {
		printf STDOUT ("skipping output at $pos since it's boring\n");
		return(0);
	}
	logit(undef,"Output of $pos");
	foreach my $oside (0,1) {
		#logit($oside,"chunk:",$$chunkref[$oside]);
		if ($$chunkref[$oside] ne "") {
			if (defined($notext)) {
				if ($notext == $oside) {
					printf STDOUT ("Problem: \\no%stext followed by \\%stext?",$sides[$notext],$sides[$oside]) ;
					printf OUT "\\p\n\\%stext\n%s",$sides[$oside],$$chunkref[$oside];
				}  else {
					printf OUT "\n%s",$$chunkref[$oside];
				}
			} else {
				printf OUT "\\p\n\\%stext\n%s",$sides[$oside],$$chunkref[$oside];
			}
			$$chunkref[$oside]="";
			$notext=undef;
		} else {
			printf OUT "\\p\\no%stext\n",$sides[$oside];
			$notext=$oside;
		}
	}
	#print OUT "----------------------------------"."\n";
}

my %modes = ( # options and their help-file description
   l => 'Left master: splitting right page at each left text paragraph',
   r => 'Right master: splitting left page at each right text paragraph',
   v => 'matching verses',
   c => 'matching chapters',
   p => 'matching paragraph breaks',
   );

my $mode='v';
my $priority_side=0;
my $cleversections=0;
my $logfile=undef;
my $outfile="-";
my $usage="\nUsage: $0 [-mode|options] LeftFile RightFile\n"
	. "Read LeftFile and RightFile, merging them according to the selected mode)\n "
	. "Mode may be any one of :\n "
	. join("\n ",map {'-'.$_." :\t".$modes{$_}.(($_ eq $mode)?" (default)":"") } (keys %modes)) . "\n"
	. "Options are:\n "
	. "-s :\tSplit off section headings at start of a chunk (makes verses line up)\n"
	. "-L file\t: Log to file\n"
	. "-o file\t: Output to file\n";
###########################
# Option parsing
###########################
while ($#ARGV>=0 and $ARGV[0]=~/^-(.)(.*)/) {
	shift;
	my ($Flag,$Rest)=($1,$2);
	my $done=0;
	do {
		if (defined($modes{$Flag})) {
			$mode=$Flag;
			#print ("Mode set to $mode\n");
		} elsif ($Flag eq 'o') {
			if ($Rest ne "") {
				$outfile=$Rest;
			} else {
				$outfile=shift;
			}
		} elsif ($Flag eq 'L') {
			if ($Rest ne "") {
				$logfile=$Rest;
			} else {
				$logfile=shift;
			}
		} elsif ($Flag eq 's') {
			$cleversections=1;
		} elsif ($Flag eq 'R') {
			my $range;
			if ($Rest ne "") {
				$range=$Rest;
			} else {
				$range=shift;
			}
			my ($startref,$stopref)=split("-",$range,2);
			if (!defined($startref) or $startref eq "") {
				$startref="0:0";
			}
			if (!defined($stopref) or $stopref eq "") {
				$stopref="999:999";
			}
			$start=ref_to_pos($startref);
			$stop=ref_to_pos($stopref);
		} else {
			print "$Flag unknown\n";
			print $usage;
			exit(1);
		}
		($Flag,$Rest)=split("",$Rest,2);
		$Rest="" if (undef($Rest));
	} while (!$done and defined($Flag) and $Flag ne "");
}

if ($#ARGV!=1) {
	print $usage;
	exit(1);
}

my ($leftfile,$rightfile)=@ARGV;


if (defined($logfile)) {
	#print ("Openning log file $logfile\n");
	open(LOG,'>',$logfile);
	$logging=1;
}

print ("Openning log file $logfile\n");
if ($outfile eq '-') {
	open(OUT,'>& STDOUT');
} else {
	open(OUT,'>',$outfile);
}

###########################
# Applying options
###########################
@leftdata=readfile($leftfile);
@rightdata=readfile($rightfile);
my $side=0;
my $otherside=1;
my @data=(\@leftdata,\@rightdata);
my @required=();
# These 'active' numbers define if the sfm is active and where code goes in the position register
if ($mode=~/[cvplr]/) {
	$active{'c'}=1;
	$active{'v'}=0;
	push @required,'\d+::\d*(?:[1-9][0-9]|[02-9]:)' # Prevent breaking at (before) verse 1
}
if ($mode=~/[vplr]/) {
	$active{'v'}=2;
}
if ($mode=~/[plr]/) {
	$active{'p'}=3;
	push @required, '[ps]';
}
my %splitcode; # places to split the other side
if ($mode=~/[lr]/) {
	$splitcode{'p'}=1;
}
my %isheading;
my @sectionheadings = qw/s s1 s2 ms mr/;
map {$isheading{$_}=1;} @sectionheadings;
map {$active{$_}=4;$splitcode{$_}=2;} @sectionheadings;
if ($mode eq 'r') {
  $priority_side=1; # default value is 0
}


logit(undef,sprintf("Configuration status is:\n  Section headers:%s\n  active SFM codes:%s\n",($cleversections?"special treatment":"ignored"),join(", ",map {$_."(".$active{$_}.")"} sort keys %active)));
my @numeric=(0,1,1,0,0,0,0); # which positions have numbers
my @hold=("",""); # interpreted things we don't want to output yet.

my @chapter;
my %breakafter;
my @chunks=(['start',''],['start','']);

#
# Classify chunks of data
#
while($#leftdata>=0 or $#rightdata>=0) {
	if ($#{$data[$side]}==-1) {
		logit($side,"End of File");
		$otherside=$side;
		$side++;
		$side%=2;
	}
	my $cl=shift(@{$data[$side]});
	my $what;
	if ($cl =~ m/^\\(\S+)/) {
		my $code=$1;
		if (!defined($code)) {
			die("problem interpreting data $cl\n");
		}
		my $oldpos;
		if (defined($active{$code})) {
			logit($side,'Interpreting code',$code);
			if ($code =~ /^[cv]$/) {
				($what)= (${$data[$side]}[0]=~m/^\s*([-0-9]+)/);
				if (!defined($what)) {
					print("Unrecognised chapter or verse in ".${$data[$side]}[0] );
				}
				if ($what=~/(\d+)-(\d+)/) { # a range.. hmm
					$what=$1;
				}
				$what=sprintf("%03d",$what);
			} elsif ($isheading{$code}) {
				$what="s";
			} else {
				$what=$code;
			}
			if ($code eq 'c') {
				$chapter[$side]=$cl . shift @{$data[$side]};
				$cl='';
			}
			my $idx=$active{$code};
			if (!defined($what)) {
				die("EH?");
			}
			#my @pos=map {if (!defined($_)) {""} else {$_} }
			my @pos=split('::',$position[$side],-$maxactive);
			#logit(undef,$idx,$what);
			$pos[$idx]=$what;
			# Incrementing chapter empties verses, and so on.
			while($idx<=$maxactive) {
				++$idx;
				if ($numeric[$idx]) {
					$pos[$idx]='000';
				} else {
					$pos[$idx]='';
				}
			}
			#logit($sides[$side],$oldpos," => ",$position[$side]);
			#logit($sides[$otherside]," = ",$position[$otherside]);
			$oldpos=$position[$side];
			$position[$side]=join('::',@pos);
			my $inr=inrange($position[$side]);
			if ($pos[2] ne '000' and !$first_inrange[$side] and $inr) {
				logit($side,"First inrange verse");
				$first_inrange[$side]=$#{$chunks[$side]}+1;
			}
			$inrange[$side]=$inr;
			if ($code eq 'v' and $inrange[$side] and (defined($chapter[$side])) ) {
				$cl=$chapter[$side].$cl;
				$chapter[$side]=undef;
			}
			if ($oldpos ne $position[$side]) {
				my $ok=1;
				# Check for oldpos being a break point, so
				# the new chunk starts after a break.
				foreach my $search (@required) {
					if ($oldpos !~ /$search/ and $position[$side] !~/$search/) {
						$ok=0;
						logit($side,$search,"not found in",$position[$side] ,"or", $oldpos);
					}
				}
				# special case: don't want to split off the
				# final \p from a section, or bad things
				# happen.

				if (($oldpos =~ /::s::/) and $position[$side] =~ /::p::/) {
					$ok=0;
				}

				if ($breakafter{$oldpos}) {
					$ok=1;
				}
				if ($ok) {
					my $idx=$#{$chunks[$side]};
					logit($side,"New chunk started",$idx-1, $position[$side]);
					${$chunks[$side]}[$idx+1]=$position[$side];
					${$chunks[$side]}[$idx+2]=$cl;
					if (($side==0 and $mode eq 'l') or ($side==1 and $mode eq 'r')) {
						$breakafter{$oldpos}=1;
					}
					next;
				}
			}

		}
	}
	my $idx=$#{$chunks[$side]};
	${$chunks[$side]}[$idx].=$cl;
	# Make sure that we read priority_side first by switching away less soon
	if ($side==$priority_side) {
		if ($position[$otherside] lt $position[$side]) {
			if ($#{$data[$otherside]} >=0 ) {
				$otherside=$side;
				$side++;
				$side%=2;
			}
		}
	} else {
		if ($position[$otherside] le $position[$side]) {
			if ($#{$data[$otherside]} >=0 ) {
				$otherside=$side;
				$side++;
				$side%=2;
			}
		}
	}
}

my $ok=1;
my ($left,$right)=@chunks;
my @combined=("","");
@position=('start','start');
my @prevposition=('','');
my @nextposition=('','');
#
#Always include the file header
#
foreach my $side (0,1) {
	if ($chunks[$side][0] eq $position[$side]) {
		$chunk[$side]=${$chunks[$side]}[1];
	}
}
do_output($position[$side],\@chunk);

# Combine chunks and output them, assuming they're still in range
# When the chunk references (positions) line up then its time for a new
# grouping.
logit(undef,sprintf("First inrange: %s,%s\n",@first_inrange));
my @idx=(@first_inrange);
my $atstart=1;
logit(undef,sprintf("First index: %s,%s\n",@idx));
# get previous position, in case of it being a heading, along with present and next positions
foreach my $side (0,1) {
	if ($idx[$side]>=2) {
		$prevposition[$side]=${$chunks[$side]}[$idx[$side]-2];
		if ($prevposition[$side]=~/::s::/) {
			$heading[$side]=$chunks[$side][$idx[$side]-1];
		}
	}
	$position[$side]=${$chunks[$side]}[$idx[$side]];
	$nextposition[$side]=${$chunks[$side]}[$idx[$side]+2];
}
my @maxidx=map {$#{$chunks[$_]}} (0,1);
#
# Main loop for output
#
if ($position[0] ne $position[1]) {
	die("Unexpected error: Starting references are not identical\n".$position[0]."!=".$position[1]);
}
while ($idx[0]<$maxidx[0] and $idx[1]<$maxidx[1]) {
	logit(undef,"Outer: L".$position[0],"R".$position[1],"Ln".$nextposition[0],"Rn".$nextposition[1]);
	#print ("Idxes:",$idx[0]," ",$idx[1]);
	my $isheading;
	# check if the previous chunk was a section heading
	$isheading=0;
	foreach my $side (0,1) {
		if ($prevposition[$side] =~ /::s::/) {
			$isheading=1;
		}
	}
	$atstart=0;
	my @combined=("","");
	if (inrange($position[$side])) {
		if ($isheading) {
			logit(undef,"Using heading(s)");
			if ($cleversections) {
				do_output($position[$side]."section",\@heading);
			} else {
				@combined=@heading;
			}
			@heading=('','');
		}

		my ($side,$otherside)=(2,2);
		if ($nextposition[0] gt $nextposition[1]) {
			$side=1;
			$otherside=0;
		} elsif ($nextposition[0] lt $nextposition[1]) {
			$side=0;
			$otherside=1;
		}
		#
		#If the loop below won't trigger for this chunk then output both chunks here
		#
		if ($nextposition[0] eq $nextposition[1]) {
			foreach my $side (0,1) {
				$combined[$side].=$heading[$side].${$chunks[$side]}[$idx[$side]+1];
				logit($side,"A",$idx[$side]);
				$idx[$side]+=2;
				$heading[$side]="";
				$prevposition[$side]=$position[$side];
				$position[$side]=$nextposition[$side];
				if (($idx[$side]+2)<=$maxidx[$side]) {
					$nextposition[$side]=${$chunks[$side]}[$idx[$side]+2];
					#printf STDERR "%s: Read idx %d=%s\n", $sides[$side], $idx[$side]+2,$nextposition[$side];
				}
			}
			logit(undef,"Outputting chunk");
			do_output($position[0],\@combined);
		} else {
			# $side will be added by loop below. First add $otherside or it'll be skipped.
			if ($position[$otherside] =~/::s::/) {
				logit($otherside,"Adding to heading");
				$heading[$otherside].=${$chunks[$otherside]}[$idx[$otherside]+1];
				logit($otherside,"Bh".$idx[$otherside]);
			} else {
				logit($otherside,"Adding chunk for output");
				$combined[$otherside].=$heading[$otherside].${$chunks[$otherside]}[$idx[$otherside]+1];
				logit($otherside,"B".$idx[$otherside]);
				$heading[$otherside]="";
			}
			$idx[$otherside]+=2;
			$prevposition[$otherside]=$position[$otherside];
			$position[$otherside]=$nextposition[$otherside];
			if (($idx[$otherside]+2)<=$maxidx[$otherside]) {
				$nextposition[$otherside]=${$chunks[$otherside]}[$idx[$otherside]+2];
				#printf STDERR "%s: Read idx %d=%s\n", $sides[$side], $idx[$side]+2,$nextposition[$side];
			} else {
				$nextposition[$otherside]='999::999::';
			}
		#
			#middle loop
			while (($position[$side] ne $position[$otherside]) and (inrange($position[$side]))  and ( $idx[$side]<$maxidx[$side])) {
				logit(undef,"Middle : L:".$position[0],"R:".$position[1],"Ln".$nextposition[0],"Rn".$nextposition[1]);
				#inner loop
				while ($position[$side] lt $position[$otherside] and inrange($position[$side]) and ($idx[$side] < $maxidx[$side])) {
					logit(undef,"Inner : L:".$position[0],"R:".$position[1],"Ln".$nextposition[0],"Rn".$nextposition[1]);
					if ($position[$side] =~/::s::/) {
						logit($side,"Adding to heading");
						$heading[$side].=${$chunks[$side]}[$idx[$side]+1];
						logit($side,"Ch".$idx[$side]);
					} else {
						logit($side,"Adding chunk for output");
						$combined[$side].=$heading[$side].${$chunks[$side]}[$idx[$side]+1];
						logit($side,"C".$idx[$side]);
						$heading[$side]="";
					}
					# Increment counter for this side
					$idx[$side]+=2;
					$prevposition[$side]=$position[$side];
					$position[$side]=$nextposition[$side];
					if (($idx[$side]+2)<=$maxidx[$side]) {
						$nextposition[$side]=${$chunks[$side]}[$idx[$side]+2];
						#printf STDERR "Read idx %d=%s\n", $idx[$side]+2,$nextposition[$side];
					} else {
						$nextposition[$side]='999::999::';
						#printf STDERR "EOD idx %d=%s\n", $idx[$side]+2,$nextposition[$side];

					}
				}
				logit($side,"Swapping sides");
				#printf STDERR ("Swapping sides %s %s\n",$position[0],$position[1]);
				$otherside=$side;
				$side++;
				$side%=2;
			} # End of Middle loop
			logit($side,"Outputting chunk");
			do_output($position[$side],\@combined);
			@combined=("","");
			#if (!inrange[$nextposition[$side]]) {
				#$idx[$side]=$#{$chunks[$side]}+1;
			#}
		}
	} else {
		@heading=("","");
		foreach my $side (0,1) {
			$idx[$side]+=2;
			$prevposition[$side]=$position[$side];
			$position[$side]=$nextposition[$side];
			if (($idx[$side]+2)<=$maxidx[$side]) {
				$nextposition[$side]=${$chunks[$side]}[$idx[$side]+2];
				#printf STDERR "%s: Read idx %d=%s\n", $sides[$side], $idx[$side]+2,$nextposition[$side];
			}
		}
	}
}
