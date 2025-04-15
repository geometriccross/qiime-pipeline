#!/bin/bash


gen_matrix() {
    for first in "$@"; do
        for second in "$@"; do
            if [ "$first" = "$second" ]; then
                continue
            fi
            if [[ "$first" > "$second" ]]; then
                pair="$second$first"
            else
                pair="$first$second"
            fi
            echo "$pair"
        done
    done | sort -u
}


ALPHA="/tmp/out/alpha"
mkdir -p "$ALPHA"
cd "$ALPHA" || exit 1

for sp in $(gen_matrix "$(awk '{ print $4 }' /tmp/meta | uniq | tail +2 | sort)"); do
	meta="/tmp/meta_$sp"
	python /scripts/extract_id.py /tmp/meta "$sp" > "$meta"

	qiime diversity alpha-group-significance \
		--quiet \
		--m-metadata-file "$meta" \
		--i-alpha-diversity "$CORE"/shannon_"$sp".qza \
		--o-visualization shannon_"$sp".qzv

	qiime diversity alpha-group-significance \
		--quiet \
		--m-metadata-file "$meta" \
		--i-alpha-diversity "$CORE"/faith_pd_"$sp".qza \
		--o-visualization faith_pd_"$sp".qzv

	qiime diversity alpha-group-significance \
		--quiet \
		--m-metadata-file "$meta" \
		--i-alpha-diversity "$CORE"/observed_features_"$sp".qza \
		--o-visualization observed_features_"$sp".qzv
done
