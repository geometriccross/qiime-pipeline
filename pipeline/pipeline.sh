#!/bin/bash

set -e -x

PRE="${OUT}/main_$(tr -dc 0-9A-Za-z < /dev/urandom | fold -w 10 | head -1)"
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
	--i-table "${PRE}/filtered_table.qza"	

# qiime feature-table tabulate-seqs \
# 	--i-data "${PRE}/resampled_table.qza" \
# 	--o-visualization "${PRE}/representative_sequences.qzv"
#
# ./pipeline/view.sh

# mkdir first/current-data
# qiime feature-table filter-samples \
# 	--p-exclude-ids \
# 	--m-metadata-file source/metadata/bat-fleas-not-reached-metadata.tsv \
# 	--i-table first/denoise/table.qza \
# 	--o-filtered-table first/current-data/current-table.qza &
#
# qiime feature-table filter-seqs \
# 	--p-exclude-ids \
# 	--m-metadata-file source/metadata/bat-fleas-not-reached-metadata.tsv \
# 	--i-data first/denoise/representative_sequences.qza \
# 	--o-filtered-data first/current-data/current-sequences.qza &
#
# # metadataも新しく作り直します。
#
# filter_script=$(
# 	cat <<-'EOF'
# 		BEGIN {
# 			split(EXCLUDE, excludes)
# 			for (e in excludes) {
# 				exclude_dict[excludes[e]] = 1
# 			}
# 		}
#
# 		# $1がexcludesになければ出力
# 		!($1 in exclude_dict) {
# 			print $0
# 		}
# 	EOF
# )
#
# awk -v EXCLUDE="${not_reached[*]}" "$filter_script" source/metadata/bat-fleas-metadata.tsv >source/metadata/bat-fleas-filtered-metadata.tsv
#
# # 以下のコマンドを実行し、確認してください。
#
# wait
#
# qiime feature-table summarize \
# 	--i-table first/current-data/current-table.qza \
# 	--o-visualization first/current-data/current-table.qzv \
# 	--m-sample-metadata-file source/metadata/bat-fleas-filtered-metadata.tsv &
#
# qiime feature-table tabulate-seqs \
# 	--i-data first/current-data/current-sequences.qza \
# 	--o-visualization first/current-data/current-sequences.qzv &
#
# # 〈Taxonomic analysisについて〉
# # 今回使うデータベースはSilvaです。
#
# qiime feature-classifier classify-sklearn \
# 	--i-classifier source/db/classifier-silva138.qza \
# 	--i-reads first/current-data/current-sequences.qza \
# 	--output-dir first/taxonomy
#
# qiime metadata tabulate \
# 	--m-input-file first/taxonomy/classification.qza \
# 	--o-visualization first/taxonomy/classification.qzv &
#
# qiime taxa barplot \
# 	--i-table first/denoise/table.qza \
# 	--i-taxonomy first/taxonomy/classification.qza \
# 	--m-metadata-file source/metadata/bat-fleas-filtered-metadata.tsv \
# 	--o-visualization first/taxonomy/taxonomy-bar-plots.qzv &
#
# # --------------------------------------------------------------------------------------------
# #!/bin/bash
# # 【はじめに】
# # 1次解析を終えて、以下のようなディレクトリになっているはずです
#
# # ├── first
# # │   ├── align-to-tree-mafft-fasttree
# # │   │   ├── alignment.qza
# # │   │   ├── masked_alignment.qza
# # │   │   ├── rooted_tree.qza
# # │   │   └── tree.qza
# # │   ├── current-data
# # │   │   ├── current-sequences.qza
# # │   │   ├── current-sequences.qzv
# # │   │   ├── current-table.qza
# # │   │   └── current-table.qzv
# # │   ├── demux
# # │   │   ├── demux-paired-end.qza
# # │   │   └── demux-paired-end.qzv
# # │   ├── denoise
# # │   │   ├── denoising_stats.qza
# # │   │   ├── denoising_stats.qzv
# # │   │   ├── representative_sequences.qza
# # │   │   ├── representative_sequences.qzv
# # │   │   ├── table.qza
# # │   │   └── table.qzv
# # │   └── taxonomy
# # │       ├── classification.qza
# # │       └── classification.qzv
# # └── source
# #     ├── batfleas-191217
# #  	|	└── たくさんのfastqファイル
# #     ├── db
# #     │   └── classifier-silva138.qza
# #     └── metadata
# #         ├── bat-fleas-filtered-metadata.tsv
# #         └── bat-fleas-metadata.tsv
#
# # このうち、今回使用するファイルは以下の通りです
# # first/current-data/current-table.qza
# # first/current-data/current-sequences.qza
# # first/taxonomy/classification.qza
# # source/metadata/bat-fleas-filtered-metadata.tsv
#
# # 【コマンドライン 2次解析】
# # 〈不必要なデータの削除〉
# # 1次解析においてCyanobacteria，Mitochondoria,Chloroplastに分類されたFeatureが確認された場合、これを除かなければなりません。
# # 以下のコマンドで削除していきます。
#
# set -e -x
#
# mkdir -p second/filtered
#
# echo "taxa filter-table" &&
# 	qiime taxa filter-table \
# 		--i-table first/current-data/current-table.qza \
# 		--i-taxonomy first/taxonomy/classification.qza \
# 		--p-exclude mitochondria,cyanobacteria \
# 		--o-filtered-table second/filtered/filtered-table.qza &
#
# qiime taxa filter-seqs \
# 	--i-sequences first/current-data/current-sequences.qza \
# 	--i-taxonomy first/taxonomy/classification.qza \
# 	--p-exclude mitochondria,cyanobacteria \
# 	--o-filtered-sequences second/filtered/filtered-sequences.qza &
#
# # 次に、削除したデータをもとにした系統樹を作成します。
#
# wait
#
# qiime phylogeny align-to-tree-mafft-fasttree \
# 	--i-sequences second/filtered/filtered-sequences.qza --output-dir second/align-to-tree-mafft-fasttree
#
# (cd second/align-to-tree-mafft-fasttree && rename.ul "" filtered- *)
#
# # ここまでのコマンドで「mitochondria」「cyanobacteria」などが除かれたデータが作成できました。
# # このデータを用いてTaxonomy解析も行います。
#
# qiime feature-classifier classify-sklearn \
# 	--i-classifier source/db/classifier-silva138.qza \
# 	--i-reads second/filtered/filtered-sequences.qza \
# 	--output-dir second/taxonomy
#
# qiime metadata tabulate \
# 	--m-input-file second/taxonomy/classification.qza \
# 	--o-visualization second/taxonomy/classification.qzv &
#
# qiime taxa barplot \
# 	--i-table second/filtered/filtered-table.qza \
# 	--i-taxonomy second/taxonomy/classification.qza \
# 	--m-metadata-file source/metadata/bat-fleas-filtered-metadata.tsv \
# 	--o-visualization second/taxonomy/taxonomy-bar-plots.qzv &
#
# # 〈多様性解析〉
# # 次に多様性解析を行うための指数を算出しましょう。
# # ここで用いる「--p-sampling-depth」は、1次解析の際に算出したものを用いてください。
#
# qiime diversity core-metrics-phylogenetic \
# 	--i-phylogeny second/align-to-tree-mafft-fasttree/filtered-rooted_tree.qza \
# 	--i-table second/filtered/filtered-table.qza \
# 	--p-sampling-depth 15000 \
# 	--m-metadata-file source/metadata/bat-fleas-filtered-metadata.tsv \
# 	--output-dir second/core-metrics-results
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
