#!/bin/bash

tmp="out/$(date +%h%d-%H-%M)_$(tr -dc 0-9A-Za-z < /dev/urandom | fold -w 10 | head -1)"
OUT="${tmp}"
unset tmp

DB="db/classifier.qza"
MANI="${OUT}/manifest"
META="${OUT}/meta"

# https://unix.stackexchange.com/questions/706602/use-getopt-to-directly-retrieve-option-value
while getopts m:c:o:f:x:s:d: OPT
do
	case $OPT in
		o)	OUT=$OPTARG;;
		d)	DB=$OPTARG;;
		c)	MANI=$OPTARG;;
		x)	META=$OPTARG;;
		s)	SAMPLING_DEPTH=$OPTARG;;
		*)	exit 1;;
	esac
done

mkdir -p "${OUT}"
./pipeline/create_Mfiles.py --id-prefix id --out-meta "${META}" --out-mani "${MANI}"
./pipeline/check_manifest.py "${MANI}"

if [ ! -f "$DB" ]; then
	dirname "${DB}" | xargs mkdir -p
	source db.sh
fi

# if variable was not set
if [ -z ${SAMPLING_DEPTH+x} ]; then
	source ./pipeline/rarefaction.sh | xargs ./pipeline/view.sh
else
	source ./pipeline/pipeline.sh
fi

