#!/bin/bash

set -ex

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

qiime taxa filter-table \
	--quiet \
	--p-exclude mitochondria,cyanobacteria \
	--i-table filtered_table.qza \
	--i-taxonomy classification.qza \
	--o-filtered-table common_biology_free_table.qza

qiime taxa filter-seqs \
	--quiet \
	--p-exclude mitochondria,cyanobacteria \
	--i-sequences filtered_seq.qza \
	--i-taxonomy classification.qza \
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

qiime taxa barplot \
	--quiet \
	--i-table common_biology_free_table.qza \
	--i-taxonomy common_biology_free_classification.qza \
	--m-metadata-file /tmp/meta \
	--o-visualization taxa-bar-plots.qzv

# ./pipeline/view.sh "${PRE}/taxa-bar-plots.qzv"

# core-metricsでoutput-dirを指定する場合、dirがすでに存在していると失敗する
CORE="/tmp/out/core"
cd /tmp/out || exit 1 # preで生成したファイルを使用するため、cwdを移動しない方が都合がよい

qiime diversity core-metrics-phylogenetic \
	--quiet \
	--m-metadata-file /tmp/meta \
	--p-sampling-depth "$SAMPLING_DEPTH" \
	--i-phylogeny ./pre/common_biology_free_rooted-tree.qza \
	--i-table ./pre/common_biology_free_table.qza \
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
