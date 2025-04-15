#!/bin/bash


ALPHA="/tmp/out/alpha"
mkdir -p "$ALPHA"
cd "$ALPHA" || exit 1


# pairs=$(awk '{ print $4 }' /tmp/meta | uniq | tail -n +2 | sort)
for (( i = 0; i < ${#pairs[@]}; i++ )); do
  for (( j = i + 1; j < ${#pairs[@]}; j++ )); do
    echo "組み合わせ: ${pairs[i]} と ${pairs[j]}"

	combi=${pairs[i]}_${pairs[j]}
	meta="/tmp/meta_$combi"

	python /scripts/extract_id.py /tmp/meta "${pairs[i]}" "${pairs[j]}"  > "$meta"

	cat "$meta"
	qiime diversity alpha-group-significance \
		--m-metadata-file "$meta" \
		--i-alpha-diversity "$CORE"/shannon_"$combi".qza \
		--o-visualization shannon_"$combi".qzv

	qiime diversity alpha-group-significance \
		--m-metadata-file "$meta" \
		--i-alpha-diversity "$CORE"/faith_pd_"$combi".qza \
		--o-visualization faith_pd_"$combi".qzv

	qiime diversity alpha-group-significance \
		--m-metadata-file "$meta" \
		--i-alpha-diversity "$CORE"/observed_features_"$combi".qza \
		--o-visualization observed_features_"$combi".qzv
  done
done
