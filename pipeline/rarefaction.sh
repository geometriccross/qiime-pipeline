#!/bin/bash

set -e

RAREFACTION_DIR="${OUT}/rare_$(tr -dc 0-9A-Za-z < /dev/urandom | fold -w 10 | head -1)"
mkdir -p "${RAREFACTION_DIR}"

qiime tools import \
	--type 'SampleData[PairedEndSequencesWithQuality]' \
	--input-format PairedEndFastqManifestPhred33V2 \
	--input-path "${MANI}" \
	--output-path "${RAREFACTION_DIR}/paired_end_demux.qza" >/dev/null

# qiime demux summarize \
# 	--quiet \
# 	--i-data "${RAREFACTION_DIR}/paired_end_demux.qza" \
# 	--o-visualization "${RAREFACTION_DIR}/paired_end_demux.qzv"

qiime dada2 denoise-paired \
	--quiet \
	--i-demultiplexed-seqs "${RAREFACTION_DIR}/paired_end_demux.qza" \
	--p-n-threads 0 \
	--p-trim-left-f 17 \
	--p-trim-left-r 21 \
	--p-trunc-len-f 250 \
	--p-trunc-len-r 250 \
	--o-table "${RAREFACTION_DIR}/denoised_table.qza" \
	--o-representative-sequences "${RAREFACTION_DIR}/denoised_seq.qza" \
	--o-denoising-stats "${RAREFACTION_DIR}/denoised_stats.qza"

# qiime feature-table summarize \
# 	--i-table first/denoise/table.qza \
# 	--o-visualization first/denoise/table.qzv \
# 	--m-sample-metadata-file source/metadata/bat-fleas-metadata.tsv &

# qiime feature-table tabulate-seqs \
# 	--i-data first/denoise/representative_sequences.qza \
# 	--o-visualization first/denoise/representative_sequences.qzv &

# qiime metadata tabulate \
# 	--m-input-file first/denoise/denoising_stats.qza \
# 	--o-visualization first/denoise/denoising_stats.qzv &

qiime phylogeny align-to-tree-mafft-fasttree \
	--quiet \
	--i-sequences "${RAREFACTION_DIR}/denoised_seq.qza" \
	--o-alignment "${RAREFACTION_DIR}/aligned-rep-seqs.qza" \
    --o-masked-alignment "${RAREFACTION_DIR}/masked-aligned-rep-seqs.qza" \
    --o-tree "${RAREFACTION_DIR}/unrooted-tree.qza" \
    --o-rooted-tree "${RAREFACTION_DIR}/rooted-tree.qza"

qiime diversity alpha-rarefaction \
	--quiet \
	--p-min-depth 1 \
	--p-max-depth 50000 \
	--m-metadata-file "${META}" \
	--i-table "${RAREFACTION_DIR}/denoised_table.qza" \
	--i-phylogeny "${RAREFACTION_DIR}/rooted-tree.qza" \
	--o-visualization "${RAREFACTION_DIR}/alpha_rarefaction.qzv"

echo "${RAREFACTION_DIR}/alpha_rarefaction.qzv"
