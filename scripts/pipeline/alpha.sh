#!/bin/bash


ALPHA="/tmp/out/alpha"
mkdir -p "$ALPHA"
cd "$ALPHA" || exit 1

set -ex
pairs=(ctenocephalides_felis ischnopsyllus_needhami lipoptena_fortisetosa pedicinus_obtusus)
for ((i = 0; i < ${#pairs[@]}; i++)); do
	target=${pairs[i]}
	meta="/tmp/meta_$target"

	dst="$ALPHA/$target"
	mkdir -p $dst
	cd $dst || exit 1

	python /scripts/extract_id.py /tmp/meta --column 3 "${pairs[i]}" > "$meta"

	qiime diversity filter-alpha-diversity \
		--i-alpha-diversity "$CORE"/shannon_vector.qza \
		--m-metadata-file "$meta" \
		--o-filtered-alpha-diversity shannon_vector_"$target".qza

	qiime diversity filter-alpha-diversity \
		--i-alpha-diversity "$CORE"/faith_pd_vector.qza \
		--m-metadata-file "$meta" \
		--o-filtered-alpha-diversity faith_pd_vector_"$target".qza

	qiime diversity filter-alpha-diversity \
		--i-alpha-diversity "$CORE"/observed_features_vector.qza \
		--m-metadata-file "$meta" \
		--o-filtered-alpha-diversity observed_features_vector_"$target".qza

	qiime diversity alpha-group-significance \
		--m-metadata-file "$meta" \
		--i-alpha-diversity shannon_vector_"$target".qza \
		--o-visualization shannon_"$target".qzv

	qiime diversity alpha-group-significance \
		--m-metadata-file "$meta" \
		--i-alpha-diversity faith_pd_vector_"$target".qza \
		--o-visualization faith_pd_"$target".qzv

	qiime diversity alpha-group-significance \
		--m-metadata-file "$meta" \
		--i-alpha-diversity observed_features_vector_"$target".qza \
		--o-visualization observed_features_"$target".qzv
done
