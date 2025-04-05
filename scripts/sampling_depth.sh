#!/bin/bash

while getopts m:c:o:f:x:s:d: OPT; do
	case $OPT in
	c) MANI=$OPTARG ;;
	x) META=$OPTARG ;;
	*) 
		echo "Arguments are required" > /dev/err
		exit 1 ;;
	esac
done

batch_id=sampling_depth_$(./scripts/idgen.sh)
docker build . -t "$batch_id"

mkdir -p "out/$batch_id"
docker run --rm sampling_depth /scripts/pipeline/rarefaction.sh \
	--mount -type=bind "$batch_id",src="$(pwd)"/fastq,dst=/fastq,readonly \
	--mount -type=bind "$batch_id",src="$(pwd)"/meta,dst=/meta,readonly \
	-c "$MANI" \
	-x "$META" |
	xargs -I FILE docker cp sampling_depth:FILE "out/$batch_id/"

	find "out/$batch_id/" -type f -name ".qzv" | \
		xargs -0 ./scripts/pipeline/view.sh  # run in the host

