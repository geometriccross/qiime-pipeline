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

ctn_id=qiime_$random
docker build . -t "$ctn_id"

mkdir -p "$HOST_OUT"
./pipeline/create_Mfiles.py --id-prefix id --out-meta "$HOST_META" --out-mani "$HOST_MANI"
./pipeline/check_manifest.py "$HOST_MANI"

if [[ ! -f "$HOST_DB" ]]; then
	dirname "$HOST_DB" | xargs mkdir -p
	docker container run --rm "$ctn_id" /pipeline/db.sh | \
		xargs -I FILE docker cp qiime:FILE "$(realpath "$HOST_DB" | dirname)"
fi

# if variable was not set
if [[ -z ${SAMPLING_DEPTH+x} ]]; then
	source ./pipeline/rarefaction.sh | xargs ./pipeline/view.sh
else
	source ./pipeline/pipeline.sh
fi
