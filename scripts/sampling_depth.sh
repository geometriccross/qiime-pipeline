#!/bin/bash

month="$(date +%b | tr '[:upper:]' '[:lower:]')"
random="$(tr -dc 0-9A-Za-z < /dev/urandom | fold -w 3 | head -1)"
unique_id=$month"$(date +%d%H%M%S)"_$random

batch_id=sampling_depth_"$unique_id"
docker build . -t "$batch_id"

mkdir -p "out/$batch_id"
docker run --rm sampling_depth /scripts/pipeline/rarefaction.sh \
	--mount -type=bind "$batch_id",src="$(pwd)"/fastq,dst=/fastq,readonly \
	--mount -type=bind "$batch_id",src="$(pwd)"/meta,dst=/meta,readonly \
	-c "$HOST_MANI" \
	-x "$HOST_META" |
	xargs -I FILE docker cp sampling_depth:FILE "out/$batch_id/"

	find "out/$batch_id/" -type f -name ".qzv" | \
		xargs -0 ./scripts/pipeline/view.sh  # run in the host

