#!/bin/bash

export OUT="out"
export DATA="fastq"

# https://unix.stackexchange.com/questions/706602/use-getopt-to-directly-retrieve-option-value
while getopts m:c:o:d: OPT
do
	case $OPT in
		o)	OUT=$2 ; shift;;
		d)	DATA=$2 ; shift;;
		m)	META=$OPTARG;;
		c)	CONF=$OPTARG;;
	esac
done
