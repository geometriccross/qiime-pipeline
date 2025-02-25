#!/bin/bash

tmp="out/$(sha256sum <(date) | cut -d ' ' -f 1)"
export OUT="${tmp}"
unset tmp

export DATA_SOURCE="fastq"
export META_SOURCE="meta"
export MANI="${OUT}/manifest.csv"
export META="${OUT}/meta.csv"

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
python pipeline/create_master_csv.py "${META_SOURCE}" > "${META}"

./pipeline/pipeline.sh
