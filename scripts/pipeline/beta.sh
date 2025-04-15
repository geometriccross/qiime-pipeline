#!/bin/bash

BETA="/tmp/out/beta"
mkdir -p "$BETA"
cd "$BETA" || exit 1

col=("Species" "Location" "SampleGender")
for item in "${col[@]}"; do
	qiime diversity beta-group-significance \
		--quiet \
		--p-pairwise \
		--m-metadata-file /tmp/meta \
		--m-metadata-column "$item" \
		--i-distance-matrix "$CORE"/weighted_unifrac_distance_matrix.qza \
		--o-visualization weighted-unifrac-distance-matrix-"${item}".qzv
done

