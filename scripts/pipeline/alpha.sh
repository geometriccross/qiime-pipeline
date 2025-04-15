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

qiime diversity alpha-group-significance \
	--quiet \
	--m-metadata-file /tmp/meta \
	--i-alpha-diversity $CORE/shannon_vector.qza \
	--o-visualization shannon_vector.qzv

qiime diversity alpha-group-significance \
	--quiet \
	--m-metadata-file /tmp/meta \
	--i-alpha-diversity $CORE/faith_pd_vector.qza \
	--o-visualization faith_pd_vector.qzv

qiime diversity alpha-group-significance \
	--quiet \
	--m-metadata-file /tmp/meta \
	--i-alpha-diversity $CORE/observed_features_vector.qza \
	--o-visualization observed_features_vector.qzv

