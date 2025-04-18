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

qiime feature-table filter-features
	--p-min-samples 25
	--p-min-frequency 100
	--i-table $BASIC/common_biology_free_table.qza
	--o-filtered-table for_ancome_table.qza

pairs=(ctenocephalides_felis ischnopsyllus_needhami lipoptena_fortisetosa pedicinus_obtusus)
for ((i = 0; i < ${#pairs[@]}; i++)); do
	for ((j = i + 1; j < ${#pairs[@]}; j++)); do
	combi=${pairs[i]}_${pairs[j]}

	dst="$ANCOME/$combi"
	mkdir -p $dst
	cd $dst || exit 1

	qiime feature-table filter-samples \
		--p-where "[Species] In (${pairs[i]}, ${pairs[j]})" \
		--m-metadata-file /tmp/meta \
		--i-table $ANCOME/for_anco_table.qza
		--o-filtered-table species_only_table.qza

	qiime composition add-pseudocount \
		--i-table species_only_table.qza \
		--o-composition-table count_added_table.qza

	qiime composition ancom \
		--i-table count_added_table.qza \
		--m-metadata-file /tmp/meta \
		--m-metadata-column Species \
		--o-visualization ancom-subject.qzv
	done
done
