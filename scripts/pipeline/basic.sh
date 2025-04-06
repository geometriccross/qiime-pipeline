#!/bin/bash

# <<<<< THIS SCRIPT PRESUMES TO RUN IN DOCKER CONTAINER >>>>>>
if [[ ! -e /.dockerenv ]]; then
	echo "Please run in an inside of container" > /dev/stderr
	exit 1
fi

while getopts s: OPT
do
	case $OPT in
		s)	SAMPLING_DEPTH=$OPTARG;;
		*)	exit 1;;
	esac
done

PRE="/tmp/out/pre"
mkdir -p "$PRE"
cd "$PRE" || exit 1

qiime tools import \
	--type 'SampleData[PairedEndSequencesWithQuality]' \
	--input-format PairedEndFastqManifestPhred33V2 \
	--input-path /tmp/mani \
	--output-path paired_end_demux.qza >/dev/null

qiime dada2 denoise-paired \
	--quiet \
	--p-n-threads 0 \
	--p-trim-left-f 17 \
	--p-trim-left-r 21 \
	--p-trunc-len-f 250 \
	--p-trunc-len-r 250 \
	--i-demultiplexed-seqs paired_end_demux.qza \
	--o-table denoised_table.qza \
	--o-representative-sequences denoised_seq.qza \
	--o-denoising-stats denoised_stats.qza

qiime feature-table filter-samples \
	--quiet \
	--p-min-frequency "$SAMPLING_DEPTH" \
	--i-table denoised_table.qza \
	--o-filtered-table filtered_table.qza

qiime feature-table filter-seqs \
	--quiet \
	--i-data denoised_seq.qza \
	--i-table filtered_table.qza \
	--o-filtered-data filtered_seq.qza

qiime feature-classifier classify-sklearn \
	--quiet \
	--i-classifier /db/classifier.qza \
	--i-reads filtered_seq.qza \
	--o-classification classification.qza

BASIC=/tmp/out/basic
mkdir -p "$BASIC"
cd "$BASIC" || exit 1

qiime taxa filter-table \
	--quiet \
	--p-exclude mitochondria,cyanobacteria \
	--i-table $PRE/filtered_table.qza \
	--i-taxonomy $PRE/classification.qza \
	--o-filtered-table common_biology_free_table.qza

qiime taxa filter-seqs \
	--quiet \
	--p-exclude mitochondria,cyanobacteria \
	--i-sequences $PRE/filtered_seq.qza \
	--i-taxonomy $PRE/classification.qza \
	--o-filtered-sequences common_biology_free_seq.qza

qiime phylogeny align-to-tree-mafft-fasttree \
	--quiet \
	--i-sequences common_biology_free_seq.qza \
	--o-alignment common_biology_free_aligned-rep-seqs.qza \
	--o-masked-alignment common_biology_free_masked-aligned-rep-seqs.qza \
	--o-tree common_biology_free_unrooted-tree.qza \
	--o-rooted-tree common_biology_free_rooted-tree.qza

qiime feature-classifier classify-sklearn \
	--quiet \
	--i-classifier /db/classifier.qza \
	--i-reads common_biology_free_seq.qza \
	--o-classification common_biology_free_classification.qza

# core-metricsでoutput-dirを指定する場合、dirがすでに存在していると失敗する
CORE="/tmp/out/core"

qiime diversity core-metrics-phylogenetic \
	--quiet \
	--m-metadata-file /tmp/meta \
	--p-sampling-depth "$SAMPLING_DEPTH" \
	--i-phylogeny common_biology_free_rooted-tree.qza \
	--i-table common_biology_free_table.qza \
	--output-dir "$CORE"

# qiime metadata tabulate \
# 	--m-input-file $CORE/faith_pd_vector.qza \
# 	--o-visualization $CORE/faith_pd_vector.qzv
# ./pipeline/view.sh "${CORE}/faith_pd_vector.qzv"

ALPHA="/tmp/out/alpha"
mkdir -p "$ALPHA"
cd "$ALPHA" || exit 1

qiime diversity alpha-group-significance \
	--m-metadata-file /tmp/meta \
	--i-alpha-diversity $CORE/shannon_vector.qza \
	--o-visualization shannon_vector.qzv

qiime diversity alpha-group-significance \
	--m-metadata-file /tmp/meta \
	--i-alpha-diversity $CORE/faith_pd_vector.qza \
	--o-visualization faith_pd_vector.qzv

qiime diversity alpha-group-significance \
	--m-metadata-file /tmp/meta \
	--i-alpha-diversity $CORE/observed_features_vector.qza \
	--o-visualization observed_features_vector.qzv

BETA="/tmp/out/beta"
mkdir -p "$BETA"
cd "$BETA" || exit 1

col=("Species" "Location" "SampleGender")
for item in "${col[@]}"; do
	qiime diversity beta-group-significance \
		--p-pairwise \
		--m-metadata-file /tmp/meta \
		--m-metadata-column "$item" \
		--i-distance-matrix $CORE/weighted_unifrac_distance_matrix.qza \
		--o-visualization weighted-unifrac-distance-matrix-"${item}".qzv
done

