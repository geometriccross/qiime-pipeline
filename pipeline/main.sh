#!/bin/bash

tmp="out/$(date +%h%d-%H-%M)_$(tr -dc 0-9A-Za-z < /dev/urandom | fold -w 10 | head -1)"
export OUT="${tmp}"
unset tmp

export FASTQ="fastq"
export META_SOURCE="meta"
export DB="db/classifier.qza"
export MANI="${OUT}/manifest"
export META="${OUT}/meta"

# https://unix.stackexchange.com/questions/706602/use-getopt-to-directly-retrieve-option-value
while getopts m:c:o:f:x:s:d: OPT
do
	case $OPT in
		o)	OUT=$OPTARG;;
		f)	FASTQ=$OPTARG;;
		m)	META_SOURCE=$OPTARG;;
		d)	DB=$OPTARG;;
		c)	MANI=$OPTARG;;
		x)	META=$OPTARG;;
		s)	SAMPLING_DEPTH=$OPTARG;;
		*)	exit 1;;
	esac
done

mkdir -p "${OUT}"
python pipeline/create_manifest.py "${FASTQ}" > "${MANI}"
python pipeline/create_master.py "${META_SOURCE}" > "${META}"

if [ ! -f "$DB" ]; then
	dirname "${DB}" | xargs mkdir -p
	echo "$DB" | xargs wget "https://bwsyncandshare.kit.edu/s/zK5zjAbsTFQRpbo/download?path=%2Fq2_24-10%2FSilva138_2&files=classifier-V34.qza" -O
fi

# if variable was not set
if [ -z ${SAMPLING_DEPTH+x} ]; then
	./pipeline/rarefaction.sh | xargs ./pipeline/view.sh
else
	./pipeline/pipeline.sh
fi

