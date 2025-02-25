#!/bin/bash

tmp="out/$(tr -dc 0-9A-Za-z < /dev/urandom | fold -w 10 | head -1)"
export OUT="${tmp}"
unset tmp

export DATA_SOURCE="fastq"
export META_SOURCE="meta"
export MANI="${OUT}/manifest"
export META="${OUT}/meta"

# https://unix.stackexchange.com/questions/706602/use-getopt-to-directly-retrieve-option-value
while getopts m:c:o:d:x: OPT
do
	case $OPT in
		o)	OUT=$2 ; shift;;
		d)	DATA_SOURCE=$2 ; shift;;
		m)	META_SOURCE=$OPTARG;;
		c)	MANI=$OPTARG;;
		x)	META=$OPTARG;;
		*)	exit 1;;
	esac
done

mkdir -p "${OUT}"
python pipeline/create_manifest.py "${DATA_SOURCE}" > "${MANI}"
python pipeline/create_master.py "${META_SOURCE}" > "${META}"

./pipeline/pipeline.sh
