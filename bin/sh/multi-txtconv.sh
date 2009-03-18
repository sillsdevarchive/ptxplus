#!/bin/bash -x

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
tmp1=$(mktemp -t "multi-txtconv.XXXX") || exit 1
tmp2=$(mktemp -t "multi-txtconv.XXXX") || { rm $tmp1; exit 1; }

# Set error trapping in case there is a failure
trap "rm -- $tmp1 $tmp2; exit" HUP INT PIPE TERM EXIT

# It is assumed that we have one or more text encoding
# conversions to do. Do the first one now
txtconv -i $input_file -o $tmp1 -t $1; shift

# Change the name of our temp files to be ready for the rest of the conversions
tmp_in="$tmp1"
tmp_out="$tmp2"

# Take the commands one at a time in the order they are in the
# command line and run them. The "$@" allows there to be spaces
# in each quoted command.
for tec_command in "$@"
do
	txtconv -i "$tmp_in" -o "$tmp_out" -t $tec_command
	tmp_var=$tmp_in
	tmp_in=$tmp_out
	tmp_out=$tmp_var
done

# Copy the results to where we need it.
cat <$tmp_in >"$output_file"
