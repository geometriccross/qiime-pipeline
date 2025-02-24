#!/bin/bash

export OUT="out"
export DATA="fastq"
export META_DIR="meta"

# META=master.csv
while getopts m:c: OPT
do
	case $OPT in
		m)	META=$OPTARG;;
		c)	CONF=$OPTARG;;
	esac
done
