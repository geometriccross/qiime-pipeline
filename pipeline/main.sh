#!/bin/bash

# default value
HOST_OUT="out/"
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

docker build . -t qiime

mkdir -p "$HOST_OUT"
./pipeline/create_Mfiles.py --id-prefix id --out-meta "$HOST_META" --out-mani "$HOST_MANI"
./pipeline/check_manifest.py "$HOST_MANI"

if [[ ! -f "$HOST_DB" ]]; then
	dirname "$HOST_DB" | xargs mkdir -p
	docker container run --rm qiime /pipeline/db.sh | \
		xargs -I FILE docker cp qiime:FILE "$(realpath "$HOST_DB" | dirname)"
fi

# if variable was not set
if [[ -z ${SAMPLING_DEPTH+x} ]]; then
	source ./pipeline/rarefaction.sh | xargs ./pipeline/view.sh
else
	source ./pipeline/pipeline.sh
fi
