#!/bin/bash

# <<<<< THIS SCRIPT PRESUMES TO RUN IN DOCKER CONTAINER >>>>>>
if [[ ! -e /.dockerenv ]]; then
	echo "Please run in an inside of container" > /dev/stderr
	exit 1
fi

while getopts o:c:x: OPT
do
	case $OPT in
		c)	MANI=$OPTARG;;
		x)	META=$OPTARG;;
		*)	exit 1;;
	esac
done

mkdir -p /tmp/out
cd /tmp/out || exit 1

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
