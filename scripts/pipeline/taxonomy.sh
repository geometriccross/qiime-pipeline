#!/bin/bash

# <<<<< THIS SCRIPT PRESUMES TO RUN IN DOCKER CONTAINER >>>>>>
if [[ ! -e /.dockerenv ]]; then
	echo "Please run in an inside of container" > /dev/stderr
	exit 1
fi

BASIC=/tmp/out/basic
TAXA=/tmp/out/taxa
mkdir -p "$TAXA"
cd "$TAXA" || exit 1

qiime taxa barplot \
	--quiet \
	--i-table $BASIC/common_biology_free_table.qza \
	--i-taxonomy $BASIC/common_biology_free_classification.qza \
	--m-metadata-file /tmp/meta \
	--o-visualization taxa-bar-plots.qzv
