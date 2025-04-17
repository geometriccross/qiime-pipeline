#!/bin/bash


ALPHA="/tmp/out/alpha"
mkdir -p "$ALPHA"
cd "$ALPHA" || exit 1

shannon="$ALPHA/shannon"
faith_pd="$ALPHA/faith_pd"
observed_featuers="$ALPHA/observed_features"

mkdir -p "$shannon"
mkdir -p "$faith_pd"
mkdir -p "$observed_featuers"

set -ex
pairs=(ctenocephalides_felis ischnopsyllus_needhami lipoptena_fortisetosa pedicinus_obtusus)
for ((i = 0; i < ${#pairs[@]}; i++)); do
	for ((j = i + 1; j < ${#pairs[@]}; j++)); do
		combi=${pairs[i]}_${pairs[j]}
		meta="/tmp/meta_$combi"

		python /scripts/extract_id.py /tmp/meta --column 3 "${pairs[i]}" "${pairs[j]}" >"$meta"

		qiime diversity filter-alpha-diversity \
			--i-alpha-diversity "$CORE"/shannon_vector.qza \
			--m-metadata-file "$meta" \
			--o-filtered-alpha-diversity $shannon/shannon_vector_"$combi".qza

		qiime diversity filter-alpha-diversity \
			--i-alpha-diversity "$CORE"/faith_pd_vector.qza \
			--m-metadata-file "$meta" \
			--o-filtered-alpha-diversity $faith_pd/faith_pd_vector_"$combi".qza

		qiime diversity filter-alpha-diversity \
			--i-alpha-diversity "$CORE"/observed_features_vector.qza \
			--m-metadata-file "$meta" \
			--o-filtered-alpha-diversity  $observed_featuers/observed_features_vector_"$combi".qza

		qiime diversity alpha-group-significance \
			--m-metadata-file "$meta" \
			--i-alpha-diversity shannon_vector_"$combi".qza \
			--o-visualization $shannon/shannon_"$combi".qzv

		qiime diversity alpha-group-significance \
			--m-metadata-file "$meta" \
			--i-alpha-diversity faith_pd_vector_"$combi".qza \
			--o-visualization $faith_pd/faith_pd_"$combi".qzv

		qiime diversity alpha-group-significance \
			--m-metadata-file "$meta" \
			--i-alpha-diversity observed_features_vector_"$combi".qza \
			--o-visualization $faith_pd/observed_features_"$combi".qzv
	done
done
