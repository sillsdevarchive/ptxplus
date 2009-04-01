#!/bin/sh

# By Tim Eves - 20090318
# This shell script will run txtconv, part of the TECkit package and
# enable it to run multiple conversions on a single text file. This may
# be needed in situations where one conversion mapping is not enough.
# Usage:
#		multi-txtconv.sh infile.txt outfile.txt table.tec [options]

# Set our input files
input_file="$1"
output_file="$2"
# Move to the command section of the input
shift 2

# Create some temporary files
tmp_area=$(mktemp -t -d "multi-txtconv.XXXX") || exit 1
# Set error trapping in case there is a failure
trap "rm -rf -- $tmp_area; exit" HUP INT PIPE TERM EXIT

# Create tmp_files
tmp1=$tmp_area/temp_1
tmp2=$tmp_area/temp_2

# Change the name of our temp files to be ready for the rest of the conversions
tmp_in="$tmp1"
tmp_out="$tmp2"
cat <"$input_file" >$tmp_in

# Take the commands one at a time in the order they are in the
# command line and run them. The "$@" allows there to be spaces
# in each quoted command.
n=3
for tec_command in "$@"
do
	txtconv -i "$tmp_in" -o "$tmp_out" -t $tec_command
	tmp_in=$tmp_out
	tmp_out=$tmp_area/temp_$n
	n=$(($n+1))
done

# Copy the results to where we need it.
cat <$tmp_in >"$output_file"
