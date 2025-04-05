#!/bin/bash

month="$(date +%b | tr '[:upper:]' '[:lower:]')"
random="$(tr -dc 0-9A-Za-z < /dev/urandom | fold -w 3 | head -1)"
unique_id=$month"$(date +%d%H%M%S)"_$random

# default value
HOST_OUT="out/$unique_id/"
HOST_DB="db/classifier.qza"
HOST_MANI="${OUT}/manifest"
HOST_META="${OUT}/meta"

# https://unix.stackexchange.com/questions/706602/use-getopt-to-directly-retrieve-option-value
while getopts m:c:o:f:x:s:d: OPT; do
	case $OPT in
	o) HOST_OUT=$OPTARG ;;
	d) HOST_DB=$OPTARG ;;
	c) HOST_MANI=$OPTARG ;;
	x) HOST_META=$OPTARG ;;
	s) SAMPLING_DEPTH=$OPTARG ;;
	*) exit 1 ;;
	esac
done

