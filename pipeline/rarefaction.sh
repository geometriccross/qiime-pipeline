#!/bin/bash

set -e

RAREFACTION_DIR="${OUT}/rare_$(tr -dc 0-9A-Za-z < /dev/urandom | fold -w 10 | head -1)"
mkdir -p "$RAREFACTION_DIR"
cd "$RAREFACTION_DIR"

qiime tools import \
	--type 'SampleData[PairedEndSequencesWithQuality]' \
	--input-format PairedEndFastqManifestPhred33V2 \
	--input-path "$MANI" \
	--output-path paired_end_demux.qza >/dev/null

qiime dada2 denoise-paired \
	--quiet \
	--i-demultiplexed-seqs paired_end_demux.qza \
	--p-n-threads 0 \
	--p-trim-left-f 17 \
	--p-trim-left-r 21 \
	--p-trunc-len-f 250 \
	--p-trunc-len-r 250 \
	--o-table denoised_table.qza \
	--o-representative-sequences denoised_seq.qza \
	--o-denoising-stats denoised_stats.qza

qiime phylogeny align-to-tree-mafft-fasttree \
	--quiet \
	--i-sequences denoised_seq.qza \
	--o-alignment aligned-rep-seqs.qza \
    --o-masked-alignment masked-aligned-rep-seqs.qza \
    --o-tree unrooted-tree.qza \
    --o-rooted-tree rooted-tree.qza

qiime diversity alpha-rarefaction \
	--quiet \
	--p-min-depth 1 \
	--p-max-depth 50000 \
	--m-metadata-file "$META" \
	--i-table denoised_table.qza \
	--i-phylogeny rooted-tree.qza \
	--o-visualization alpha_rarefaction.qzv

realpath alpha_rarefaction.qzv
