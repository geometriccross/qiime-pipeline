#!/bin/bash

# <<<<< THIS SCRIPT PRESUMES TO RUN IN DOCKER CONTAINER >>>>>>
if [[ ! -e /.dockerenv ]]; then
	echo "Please run in an inside of container" > /dev/stderr
	exit 1
fi

BASIC=/tmp/out/basic
ANCOME="/tmp/out/ancome"
mkdir -p "$ANCOME"
cd "$ANCOME" || exit 1

# taxonomy解析で生成したtableを用いる
# qiime feature-table filter-samples \
# 	--p-where "[Species]='*'" \
# 	--m-metadata-file /tmp/meta \
# 	--i-table $BASIC/common_biology_free_table.qza  \
# 	--o-filtered-table species_only_table.qza

qiime composition add-pseudocount \
	--i-table $BASIC/common_biology_free_table.qza  \
	--o-composition-table count_added_table.qza

qiime composition ancom \
	--i-table count_added_table.qza \
	--m-metadata-file /tmp/meta \
	--m-metadata-column Species \
	--o-visualization ancom-subject.qzv
