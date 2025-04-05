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

img_id=qiime_$random
docker build . -t "$img_id"

mkdir -p "$HOST_OUT"
./pipeline/create_Mfiles.py --id-prefix id --out-meta "$HOST_META" --out-mani "$HOST_MANI"
./pipeline/check_manifest.py "$HOST_MANI"

if [[ ! -f "$HOST_DB" ]]; then
	dirname "$HOST_DB" | xargs mkdir -p
	docker run --rm "$img_id" /pipeline/db.sh | \
		docker cp qiime:- "$(realpath "$HOST_DB" | xargs dirname)"
fi

# if variable was not set
if [[ -z ${SAMPLING_DEPTH+x} ]]; then
	ctn_output="$(docker run --rm "$img_id" /pipeline/rarefaction.sh \
		-o "$HOST_OUT" \
		-c "$HOST_MANI" \
		-x "$HOST_META")"
	docker cp "$img_id":"$ctn_output" "$HOST_OUT"
	./pipeline/view.sh "$HOST_OUT"/"$(basename "$ctn_output")"# run in the host
else
	docker run --rm "$img_id" /pipeline/pipeline.sh \
		-o "$HOST_OUT" \
		-c "$HOST_MANI" \
		-x "$HOST_META" \
		-d "$HOST_DB" \
		-s "$SAMPLING_DEPTH"

	# ディレクトリの中身をHOST_OUTにコピーする
	# ディレクトリ自体がそのままHOST_OUT内部にコピーされるわけではない
	docker cp "$img_id":"/out/." "$HOST_OUT"
fi
