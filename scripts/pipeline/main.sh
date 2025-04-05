#!/bin/bash

# <<<<< THIS SCRIPT PRESUMES TO RUN IN DOCKER CONTAINER >>>>>>

if [[ ! -e /.dockerenv ]]; then
	echo "Please run in an inside of container" > /dev/stderr
	exit 1
fi

while getopts m:c:o:f:x:s:d: OPT; do
	case $OPT in
	o) CTN_OUT=$OPTARG ;;
	d) CTN_DB=$OPTARG ;;
	c) CTN_MANI=$OPTARG ;;
	x) CTN_META=$OPTARG ;;
	s) SAMPLING_DEPTH=$OPTARG ;;
	*) exit 1 ;;
	esac
done

mkdir -p "$CTN_OUT"
./pipeline/create_Mfiles.py --id-prefix id --out-meta "$CTN_META" --out-mani "$CTN_MANI"
./pipeline/check_manifest.py "$CTN_MANI"

if [[ ! -f "$CTN_DB" ]]; then
	dirname "$CTN_DB" | xargs mkdir -p
	docker run --rm "$img_id" /pipeline/db.sh | \
		docker cp qiime:- "$(realpath "$CTN_DB" | xargs dirname)"
fi

# if variable was not set
if [[ -z ${SAMPLING_DEPTH+x} ]]; then
	ctn_output="$(docker run --rm "$img_id" /pipeline/rarefaction.sh \
		-o "$CTN_OUT" \
		-c "$CTN_MANI" \
		-x "$CTN_META")"
	docker cp "$img_id":"$ctn_output" "$CTN_OUT"
	./pipeline/view.sh "$CTN_OUT"/"$(basename "$ctn_output")"# run in the host
else
	docker run --rm "$img_id" /pipeline/pipeline.sh \
		-o "$CTN_OUT" \
		-c "$CTN_MANI" \
		-x "$CTN_META" \
		-d "$CTN_DB" \
		-s "$SAMPLING_DEPTH"

	# ディレクトリの中身をCTN_OUTにコピーする
	# ディレクトリ自体がそのままCTN_OUT内部にコピーされるわけではない
	docker cp "$img_id":"/out/." "$CTN_OUT"
fi
