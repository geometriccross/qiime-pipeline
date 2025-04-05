#!/bin/bash



while getopts m:c:o:f:x:s:d: OPT; do
	case $OPT in
	s) SAMPLING_DEPTH=$OPTARG ;;
	*) exit 1 ;;
	esac
done

