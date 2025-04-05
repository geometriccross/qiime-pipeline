#!/bin/bash

set -ex

while getopts di: OPT; do
	case $OPT in
	i)
		BATCH_ID=$OPTARG
		;;
	*)
		;;
	esac
done

de '/scripts/pipeline/rarefaction.sh -c /tmp/mani -x /tmp/meta' |
	tr -d "'\r\n" | # remove CRLR and single quote
	xargs -I FILE docker cp "$BATCH_ID":FILE "out/$BATCH_ID/"

find "out/$BATCH_ID/" -type f -name "*.qzv" -print0 |
	xargs -0 ./scripts/view.sh # run in the host

