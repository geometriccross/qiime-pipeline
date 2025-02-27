#!/bin/bash

set -e -x

PRE="${OUT}/pre_$(tr -dc 0-9A-Za-z < /dev/urandom | fold -w 10 | head -1)"
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
    --p-min-frequency "${SAMPLING_DEPTH}" \
    --i-table "${PRE}/denoised_table.qza" \
    --o-filtered-table "${PRE}/filtered_table.qza"

qiime feature-table filter-seqs \
	--i-data "${PRE}/denoised_seq.qza" \
	--i-table "${PRE}/filtered_table.qza" \
	--o-filtered-data "${PRE}/filtered_seq.qza"

qiime feature-classifier classify-sklearn \
	--i-classifier "${DB}" \
	--i-reads "${PRE}/filtered_seq.qza" \
	--o-classification "${PRE}/classification.qza"

qiime taxa filter-table \
	--p-exclude mitochondria,cyanobacteria \
	--i-table "${PRE}/filtered_table.qza" \
	--i-taxonomy "${PRE}/classification.qza" \
	--o-filtered-table "${PRE}/common_biology_free_table.qza"

qiime taxa filter-seqs \
	--p-exclude mitochondria,cyanobacteria \
	--i-sequences "${PRE}/filtered_seq.qza" \
	--i-taxonomy "${PRE}/classification.qza" \
	--o-filtered-sequences "${PRE}/common_biology_free_seq.qza"

qiime phylogeny align-to-tree-mafft-fasttree \
	--i-sequences "${PRE}/common_biology_free_seq.qza" \
	--o-alignment "${PRE}/common_biology_free_aligned-rep-seqs.qza" \
    --o-masked-alignment "${PRE}/common_biology_free_masked-aligned-rep-seqs.qza" \
    --o-tree "${PRE}/common_biology_free_unrooted-tree.qza" \
    --o-rooted-tree "${PRE}/common_biology_free_rooted-tree.qza"

qiime feature-classifier classify-sklearn \
	--i-classifier "${DB}" \
	--i-reads "${PRE}/common_biology_free_seq.qza" \
	--o-classification "${PRE}/common_biology_free_classification.qza"

CORE="${OUT}/core_$(tr -dc 0-9A-Za-z < /dev/urandom | fold -w 10 | head -1)"

qiime diversity core-metrics-phylogenetic \
	--m-metadata-file "${META}" \
	--p-sampling-depth "${SAMPLING_DEPTH}" \
	--i-phylogeny "${PRE}/common_biology_free_rooted-tree.qza" \
	--i-table "${PRE}/common_biology_free_table.qza" \
	--output-dir "${CORE}"
#
# # 成功すれば、「core-metrics-result」というフォルダが作成されるはずです。
# # この中身にはα多様性解析の指数となる「shannon_vector.qza」や、β多様性解析の指数となる「jaccard_distance_matrix.qza」など重要なファイルたちが入っています。
# # では、α多様性解析の指数たち使用し、解析を行ってみましょう。
# # まず最初に「shannon_vector.qza」を用います。
#
# qiime diversity alpha-group-significance \
# 	--i-alpha-diversity second/core-metrics-results/shannon_vector.qza \
# 	--o-visualization second/core-metrics-results/shannon_vector.qzv \
# 	--m-metadata-file source/metadata/bat-fleas-filtered-metadata.tsv &
#
# # 次に「faith_pd_vector.qza」を使います。
#
# qiime diversity alpha-group-significance \
# 	--i-alpha-diversity second/core-metrics-results/faith_pd_vector.qza \
# 	--o-visualization second/core-metrics-results/faith_pd_vector.qzv \
# 	--m-metadata-file source/metadata/bat-fleas-filtered-metadata.tsv &
#
# # 最後に「observed_otus_vector.qza」を用いて解析を行います。
#
# qiime diversity alpha-group-significance \
# 	--i-alpha-diversity second/core-metrics-results/observed_otus_vector.qza \
# 	--o-visualization second/core-metrics-results/observed_otus_vector.qzv \
# 	--m-metadata-file source/metadata/bat-fleas-filtered-metadata.tsv &
#
# # 今度はβ多様性解析の指数を用いて解析を行いましょう。
# # β多様性解析では、メタデータの列部分に着目して解析を行います。
# # 用いるファイルは「weighted_unifrac_distance_matrix.qza」、metadataの列は「HostGender」です。
#
# qiime diversity beta-group-significance \
# 	--p-pairwise \
# 	--i-distance-matrix second/core-metrics-results/weighted_unifrac_distance_matrix.qza \
# 	--o-visualization second/core-metrics-results/weighted-unifrac-distance-matrix-host_gender.qzv \
# 	--m-metadata-file source/metadata/bat-fleas-filtered-metadata.tsv \
# 	--m-metadata-column HostGender &
#
# # 次に、「HostIDNo」についてのβ多様性解析を行いましょう。
# # HostIDNoの列には、値が一つしかないものがあります。このような値はβ多様性解析にかけられません。
# # このようなデータを1次解析でも行ったように、データを削除していきます。
# # まず最初に、metadataを、HostIDNoの重複数が1以上かどうかで分けます。
#
# # 重複数が2個以上のもの
# awk 'BEGIN {FS=OFS="\t"}
# 	NR==1 {print; next}
# 	{
# 	    count[$19]++
# 	    lines[$19,count[$19]] = $0
# 	}
# 	END {
# 	    for (val in count) {
# 	        if (count[val] > 1) {
# 	            for (i=1; i<=count[val]; i++) {
# 	                print lines[val,i]
# 	            }
# 	        }
# 	    }
# 	}' source/metadata/bat-fleas-metadata.tsv >source/metadata/bat-fleas-not-unique-metadata.tsv
#
# # 重複数が1個のもの
# awk 'BEGIN {FS=OFS="\t"}
# 	NR==1 {print; next}
# 	{
# 		count[$19]++
# 	    lines[$19] = $0
# 	}
# 	END {
# 		for (val in count) {
# 			if (count[val] == 1) {
# 				print lines[val]
# 			}
# 		}
# 	}' source/metadata/bat-fleas-metadata.tsv >source/metadata/bat-fleas-unique-metadata.tsv
#
# # 次に、tableとsequenceから重複数1のデータを削除します。
#
# mkdir second/tuned-host-id
# qiime feature-table filter-samples \
# 	--p-exclude-ids \
# 	--m-metadata-file source/metadata/bat-fleas-unique-metadata.tsv \
# 	--i-table second/filtered/filtered-table.qza \
# 	--o-filtered-table second/tuned-host-id/tuned-host-id-table.qza &
#
# qiime feature-table filter-seqs \
# 	--p-exclude-ids \
# 	--m-metadata-file source/metadata/bat-fleas-not-reached-metadata.tsv \
# 	--i-data second/filtered/filtered-sequences.qza \
# 	--o-filtered-data second/tuned-host-id/tuned-host-id-sequences.qza &
#
# # 次にrooted_treeを作成しましょう。
#
# wait
#
# qiime phylogeny align-to-tree-mafft-fasttree \
# 	--i-sequences second/filtered/filtered-sequences.qza --output-dir second/tuned-host-id-tree
#
# (cd second/tuned-host-id-tree && rename.ul "" tuned-host-id- *)
#
# # このコマンドが成功すれば、source/metadataフォルダ以下に「bat-fleas-not-unique-metadata.tsv」が作成されているはずです。
# # こちらのデータに合わせて再びcore-metrics-phylogeneticを作成します
# # このファイルを用いて、解析を行います。
#
# qiime diversity core-metrics-phylogenetic \
# 	--i-phylogeny second/tuned-host-id-tree/tuned-host-id-rooted_tree.qza \
# 	--i-table second/tuned-host-id/tuned-host-id-table.qza \
# 	--output-dir second/core-metrics-results-not-unique \
# 	--m-metadata-file source/metadata/bat-fleas-not-unique-metadata.tsv \
# 	--p-sampling-depth 15000
#
# qiime diversity beta-group-significance \
# 	--p-pairwise \
# 	--i-distance-matrix second/core-metrics-results-not-unique/weighted_unifrac_distance_matrix.qza \
# 	--o-visualization second/core-metrics-results-not-unique/weighted_unifrac_distance_matrix-host-id-no.qzv \
# 	--m-metadata-file source/metadata/bat-fleas-not-unique-metadata.tsv \
# 	--m-metadata-column HostIDNo
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
