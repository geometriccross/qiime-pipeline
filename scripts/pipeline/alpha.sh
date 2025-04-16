#!/bin/bash


ALPHA="/tmp/out/alpha"
mkdir -p "$ALPHA"
cd "$ALPHA" || exit 1

set -ex

pairs=(ctenocephalides_felis ischnopsyllidae_needhami lipoptena_fortisetosa pedicinus_obtusus)
for ((i = 0; i < ${#pairs[@]}; i++)); do
	for ((j = i + 1; j < ${#pairs[@]}; j++)); do
		combi=${pairs[i]}_${pairs[j]}
		meta="/tmp/meta_$combi"

		python /scripts/extract_id.py /tmp/meta --column 3 "${pairs[i]}" "${pairs[j]}" >"$meta"

		qiime diversity alpha-group-significance \
			--m-metadata-file "$meta" \
			--i-alpha-diversity "$CORE"/shannon_vector.qza \
			--o-visualization shannon_"$combi".qzv

		qiime diversity alpha-group-significance \
			--m-metadata-file "$meta" \
			--i-alpha-diversity "$CORE"/faith_pd_vector.qza \
			--o-visualization faith_pd_"$combi".qzv

		qiime diversity alpha-group-significance \
			--m-metadata-file "$meta" \
			--i-alpha-diversity "$CORE"/observed_features_vector.qza \
			--o-visualization observed_features_"$combi".qzv
	done
done
