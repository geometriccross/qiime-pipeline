#!/bin/bash

unique_id=$(idgen.sh)

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

img_id=qiime_"$unique_id"
docker build . -t "$img_id"

if [[ ! -f "$HOST_DB" ]]; then
	docker run --rm "$img_id" /scripts/pipeline/db.sh | \
		xargs -I FILE docker cp qiime:FILE "$(realpath "$HOST_DB" | xargs dirname)/" # append / for it be treated by directory
fi

if [[ -z ${SAMPLING_DEPTH+x} ]]; then
	ctn_output="$(docker run --rm "$img_id" /scripts/pipeline/rarefaction.sh \
		-o "$HOST_OUT" \
		-c "$HOST_MANI" \
		-x "$HOST_META")"
	docker cp "$img_id":"$ctn_output" "$CTN_OUT"
	./pipeline/view.sh "$CTN_OUT"/"$(basename "$ctn_output")"# run in the host
else
	docker run --rm "$img_id" /scripts/pipeline/taxonomy.sh \
		-o "$HOST_OUT" \
		-c "$HOST_MANI" \
		-x "$HOST_META" \
		-d "$HOST_DB" \
		-s "$SAMPLING_DEPTH"

	# ディレクトリの中身をHOST_OUTにコピーする
	# ディレクトリ自体がそのままHOST_OUT内部にコピーされるわけではない
	docker cp "$img_id":"/out/." "$HOST_OUT"
fi
