#!/bin/bash

set -e -x

PRE="${OUT}/pre_$(tr -dc 0-9A-Za-z </dev/urandom | fold -w 10 | head -1)"
mkdir -p "${PRE}"

qiime tools import \
	--type 'SampleData[PairedEndSequencesWithQuality]' \
	--input-format PairedEndFastqManifestPhred33V2 \
	--input-path "${MANI}" \
	--output-path "${PRE}/paired_end_demux.qza" >/dev/null

qiime dada2 denoise-paired \
	--quiet \
	--p-n-threads 0 \
	--p-trim-left-f 17 \
	--p-trim-left-r 21 \
	--p-trunc-len-f 250 \
	--p-trunc-len-r 250 \
	--i-demultiplexed-seqs "${PRE}/paired_end_demux.qza" \
	--o-table "${PRE}/denoised_table.qza" \
	--o-representative-sequences "${PRE}/denoised_seq.qza" \
	--o-denoising-stats "${PRE}/denoised_stats.qza"

qiime feature-table filter-samples \
	--quiet \
	--p-min-frequency "${SAMPLING_DEPTH}" \
	--i-table "${PRE}/denoised_table.qza" \
	--o-filtered-table "${PRE}/filtered_table.qza"

qiime feature-table filter-seqs \
	--quiet \
	--i-data "${PRE}/denoised_seq.qza" \
	--i-table "${PRE}/filtered_table.qza" \
	--o-filtered-data "${PRE}/filtered_seq.qza"

qiime feature-classifier classify-sklearn \
	--quiet \
	--i-classifier "${DB}" \
	--i-reads "${PRE}/filtered_seq.qza" \
	--o-classification "${PRE}/classification.qza"

qiime taxa filter-table \
	--quiet \
	--p-exclude mitochondria,cyanobacteria \
	--i-table "${PRE}/filtered_table.qza" \
	--i-taxonomy "${PRE}/classification.qza" \
	--o-filtered-table "${PRE}/common_biology_free_table.qza"

qiime taxa filter-seqs \
	--quiet \
	--p-exclude mitochondria,cyanobacteria \
	--i-sequences "${PRE}/filtered_seq.qza" \
	--i-taxonomy "${PRE}/classification.qza" \
	--o-filtered-sequences "${PRE}/common_biology_free_seq.qza"

qiime phylogeny align-to-tree-mafft-fasttree \
	--quiet \
	--i-sequences "${PRE}/common_biology_free_seq.qza" \
	--o-alignment "${PRE}/common_biology_free_aligned-rep-seqs.qza" \
	--o-masked-alignment "${PRE}/common_biology_free_masked-aligned-rep-seqs.qza" \
	--o-tree "${PRE}/common_biology_free_unrooted-tree.qza" \
	--o-rooted-tree "${PRE}/common_biology_free_rooted-tree.qza"

qiime feature-classifier classify-sklearn \
	--quiet \
	--i-classifier "${DB}" \
	--i-reads "${PRE}/common_biology_free_seq.qza" \
	--o-classification "${PRE}/common_biology_free_classification.qza"

qiime taxa barplot \
	--quiet \
	--i-table "${PRE}/common_biology_free_table.qza" \
	--i-taxonomy "${PRE}/common_biology_free_classification.qza" \
	--m-metadata-file "${META}" \
	--o-visualization "${PRE}/taxa-bar-plots.qzv"

# ./pipeline/view.sh "${PRE}/taxa-bar-plots.qzv"

CORE="${OUT}/core_$(tr -dc 0-9A-Za-z </dev/urandom | fold -w 10 | head -1)"

qiime diversity core-metrics-phylogenetic \
	--quiet \
	--m-metadata-file "${META}" \
	--p-sampling-depth "${SAMPLING_DEPTH}" \
	--i-phylogeny "${PRE}/common_biology_free_rooted-tree.qza" \
	--i-table "${PRE}/common_biology_free_table.qza" \
	--output-dir "${CORE}"

qiime metadata tabulate \
	--m-input-file "${CORE}/faith_pd_vector.qza" \
	--o-visualization "${CORE}/faith_pd_vector.qzv"

# ./pipeline/view.sh "${CORE}/faith_pd_vector.qzv"

ALPHA="${OUT}/alpha_$(tr -dc 0-9A-Za-z </dev/urandom | fold -w 10 | head -1)"
mkdir -p "${ALPHA}"
qiime diversity alpha-group-significance \
	--m-metadata-file "${META}" \
	--i-alpha-diversity "${CORE}/shannon_vector.qza" \
	--o-visualization "${ALPHA}/shannon_vector.qzv"

qiime diversity alpha-group-significance \
	--m-metadata-file "${META}" \
	--i-alpha-diversity "${CORE}/faith_pd_vector.qza" \
	--o-visualization "${ALPHA}/faith_pd_vector.qzv"

qiime diversity alpha-group-significance \
	--m-metadata-file "${META}" \
	--i-alpha-diversity "${CORE}/observed_features_vector.qza" \
	--o-visualization "${ALPHA}/observed_features_vector.qzv"

BETA="${OUT}/beta_$(tr -dc 0-9A-Za-z </dev/urandom | fold -w 10 | head -1)"
mkdir -p "${BETA}"

# metadataにあるヘッダーを取得し、「,」をスペースに変換
header="$(
	head -1 meta/bat_fleas.csv |
		sed 's/#SampleID//g' |
		sed 's/SampleID//g' |
		tr "," " "
)"
echo header:"${header}"

col=("${header[*]}")
echo "${col[@]}"

# SampleID, RawIDを除く
index=0
for item in "${col[@]}"; do
	# skip first column
	if [ $index != 0 ]; then
		qiime diversity beta-group-significance \
			--p-pairwise \
			--m-metadata-file "${META}" \
			--m-metadata-column "${item}" \
			--i-distance-matrix "${CORE}/weighted_unifrac_distance_matrix.qza" \
			--o-visualization "${BETA}/weighted-unifrac-distance-matrix-${item}.qzv"
	fi
	((index = index + 1))
done

# # -----------------------------------------------------------------------------------------------------------
# #!/bin/bash
# # 【はじめに】
# # 2次解析で生成したデータをもとにHeatmapを作成していきます。
# #
# # 【コマンドライン 3次解析】
# # 各サンプルのOTUとその数をTaxonomic levelごとに確認していきます。
# # 以下のコマンドをまとめてコピペし、実行してください。
#
# set -e -x
#
# mkdir third
#
# for level in 6 4 3; do
# 	echo level "$level", start
#
# 	mkdir third/collapse"$level"
# 	path=third/collapse"$level"
#
# 	if qiime taxa collapse \
# 		--p-level "$level" \
# 		--i-table second/filtered/filtered-table.qza \
# 		--i-taxonomy second/taxonomy/classification.qza \
# 		--o-collapsed-table "$path"/collapse"$level"-table.qza &&
# 		qiime composition add-pseudocount \
# 			--i-table third/collapse"$level"/collapse"$level"-table.qza \
# 			--o-composition-table "$path"/collapse"$level"-composition.qza; then
#
# 		qiime feature-table heatmap \
# 			--i-table "$path"/collapse"$level"-table.qza \
# 			--o-visualization "$path"/heatmap"$level"-HostGender.qzv \
# 			--m-metadata-file source/metadata/bat-fleas-filtered-metadata.tsv \
# 			--m-metadata-column HostGender &
#
# 		qiime feature-table heatmap \
# 			--i-table "$path"/collapse"$level"-table.qza \
# 			--o-visualization "$path"/heatmap"$level"-HostIDNo.qzv \
# 			--m-metadata-file source/metadata/bat-fleas-filtered-metadata.tsv \
# 			--m-metadata-column HostIDNo &
#
# 		qiime tools export --input-path "$path"/collapse"$level"-composition.qza --output-path "$path"/export &&
# 			mv "$path"/export/feature-table.biom $path"/feature-table.biom"
#
# 		biom convert -i "$path"/feature-table.biom -o "$path"/level"$level"-otu-taxonomic.tsv --to-tsv
# 	fi
#
# 	echo -e "level $level, finish\n"
# done
#
# # これですべての解析が終了しました。
# # 最後に今まで生成したすべてのファイルに、解析が終了した日付を付けます。
# # 次のコマンドを実行してください。
#
# wait
#
# find first second third -print0 -name "*.qz[av]" |
# 	xargs -0 rename.ul --verbose -- ".qz" "-$(date "+%y%m%d").qz"
