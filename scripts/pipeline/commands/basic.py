#!/usr/bin/env python
# flake8: noqa

from scripts.pipeline import support


class basic_pipeline(support.Pipeline):
    def __init__(self, context: support.PipelineContext):
        self._context = context

    def command_list(self) -> tuple[support.Q2CmdAssembly, str, list[str]]:
        output = self._context.setting.container_data.output_path.ctn_pos

        pre_dir = output / "pre"
        core_dir = output / "core"
        alpha_dir = output / "alpha"
        beta_dir = output / "beta"

        requires = support.RequiresDirectory()
        requires.add(output)
        requires.add(pre_dir)
        requires.add(core_dir)
        requires.add(alpha_dir)
        requires.add(beta_dir)

        # region Preprocessing
        assembly = support.Q2CmdAssembly()
        imported = (
            assembly.new_cmd("qiime tools import")
            .add_option("type", "SampleData[PairedEndSequencesWithQuality]")
            .add_option("input-format", "PairedEndFastqManifestPhred33V2")
            .add_option("input-path", self._context.ctn_manifest)
            .add_option("output-path", pre_dir / "paired_end_demux.qza")
            .get_outputs()
        )

        dataset = next(iter(self._context.setting.datasets.sets))
        region = dataset.region

        denoised_seq, denoised_table, denoised_stat = (
            assembly.new_cmd("qiime dada2 denoise-paired")
            .add_option("quiet")
            .add_input("demultiplexed-seqs", imported)
            .add_parameter("n-threads", "0")
            .add_parameter("trim-left-f", str(region.trim_left_f))
            .add_parameter("trim-left-r", str(region.trim_left_r))
            .add_parameter("trunc-len-f", str(region.trunc_len_f))
            .add_parameter("trunc-len-r", str(region.trunc_len_r))
            .add_output("representative-sequences", pre_dir / "denoised_seq.qza")
            .add_output("table", pre_dir / "denoised_table.qza")
            .add_output("denoising-stats", pre_dir / "denoised_stats.qza")
            .get_outputs()
        )

        sampling_depth = self._context.setting.sampling_depth

        filtered_table = (
            assembly.new_cmd("qiime feature-table filter-samples")
            .add_option("quiet")
            .add_input("table", denoised_table)
            .add_parameter("min-frequency", str(sampling_depth))
            .add_output("filtered-table", pre_dir / "filtered_table.qza")
            .get_outputs()
        )

        filtered_seq = (
            assembly.new_cmd("qiime feature-table filter-seqs")
            .add_option("quiet")
            .add_input("data", denoised_seq)
            .add_input("table", filtered_table)
            .add_output("filtered-data", pre_dir / "filtered_seq.qza")
            .get_outputs()
        )

        db_path = self._context.setting.container_data.database_path.ctn_pos

        classfied = (
            assembly.new_cmd("qiime feature-classifier classify-sklearn")
            .add_option("quiet")
            .add_input("classifier", db_path)
            .add_input("reads", filtered_seq)
            .add_output("classification", pre_dir / "classification.qza")
            .get_outputs()
        )

        bio_free_seq = (
            assembly.new_cmd("qiime taxa filter-seqs")
            .add_option("quiet")
            .add_parameter("exclude", "mitochondria,cyanobacteria")
            .add_input("sequences", filtered_seq)
            .add_input("taxonomy", classfied)
            .add_output("filtered-sequences", output / "common_biology_free_seq.qza")
            .get_outputs()
        )

        bio_free_table = (
            assembly.new_cmd("qiime taxa filter-table")
            .add_option("quiet")
            .add_parameter("exclude", "mitochondria,cyanobacteria")
            .add_input("table", filtered_table)
            .add_input("taxonomy", classfied)
            .add_output("filtered-table", output / "common_biology_free_table.qza")
            .get_outputs()
        )

        align_seq, masked_align_seq, unrooted_tree, rooted_tree = (
            assembly.new_cmd("qiime phylogeny align-to-tree-mafft-fasttree")
            .add_option("quiet")
            .add_input("sequences", bio_free_seq)
            .add_output(
                "alignment", output / "common_biology_free_aligned-rep-seqs.qza"
            )
            .add_output(
                "masked-alignment",
                output / "common_biology_free_masked-aligned-rep-seqs.qza",
            )
            .add_output("tree", output / "common_biology_free_unrooted-tree.qza")
            .add_output("rooted-tree", output / "common_biology_free_rooted-tree.qza")
            .get_outputs()
        )

        bio_free_classfied = (
            assembly.new_cmd("qiime feature-classifier classify-sklearn")
            .add_option("quiet")
            .add_input("classifier", db_path)
            .add_input("reads", bio_free_seq)
            .add_output(
                "classification", output / "common_biology_free_classification.qza"
            )
            .get_outputs()
        )
        # endregion

        core_metrics_files = (
            assembly.new_cmd("qiime diversity core-metrics-phylogenetic")
            .add_option("quiet")
            .add_input("phylogeny", rooted_tree)
            .add_input("table", bio_free_table)
            .add_metadata("metadata-file", self._context.ctn_metadata)
            .add_parameter("sampling-depth", str(sampling_depth))
            .add_output("rarefied-table", core_dir / "rarefied_table.qza")
            .add_output("faith-pd-vector", core_dir / "faith_pd_vector.qza")
            .add_output(
                "observed-features-vector", core_dir / "observed_features_vector.qza"
            )
            .add_output("shannon-vector", core_dir / "shannon_vector.qza")
            .add_output("evenness-vector", core_dir / "evenness_vector.qza")
            .add_output(
                "unweighted-unifrac-distance-matrix",
                core_dir / "unweighted_unifrac_distance_matrix.qza",
            )
            .add_output(
                "weighted-unifrac-distance-matrix",
                core_dir / "weighted_unifrac_distance_matrix.qza",
            )
            .add_output(
                "jaccard-distance-matrix", core_dir / "jaccard_distance_matrix.qza"
            )
            .add_output(
                "bray-curtis-distance-matrix",
                core_dir / "bray_curtis_distance_matrix.qza",
            )
            .add_output(
                "unweighted-unifrac-pcoa-results",
                core_dir / "unweighted_unifrac_pcoa_results.qza",
            )
            .add_output(
                "weighted-unifrac-pcoa-results",
                core_dir / "weighted_unifrac_pcoa_results.qza",
            )
            .add_output("jaccard-pcoa-results", core_dir / "jaccard_pcoa_results.qza")
            .add_output(
                "bray-curtis-pcoa-results", core_dir / "bray_curtis_pcoa_results.qza"
            )
            .add_output(
                "unweighted-unifrac-emperor",
                core_dir / "unweighted_unifrac_emperor.qzv",
            )
            .add_output(
                "weighted-unifrac-emperor", core_dir / "weighted_unifrac_emperor.qzv"
            )
            .add_output("jaccard-emperor", core_dir / "jaccard_emperor.qzv")
            .add_output("bray-curtis-emperor", core_dir / "bray_curtis_emperor.qzv")
            .get_outputs()
        )
        # endregion

        # region Alpha Diversity Analysis
        for name, alpha_index in {
            "observed": core_dir / "observed_features_vector.qza",
            "shannon": core_dir / "shannon_vector.qza",
            "faith_pd": core_dir / "faith_pd_vector.qza",
        }.items():
            filtered = (
                assembly.new_cmd("qiime diversity filter-alpha-diversity")
                .add_input("alpha-diversity", alpha_index)
                .add_metadata("metadata-file", self._context.ctn_metadata)
                .add_output(
                    "filtered-alpha-diversity", alpha_dir / f"filtered_{name}.qza"
                )
                .get_outputs()
            )

            alpha_visualized = (
                assembly.new_cmd("qiime diversity alpha-group-significance")
                .add_input("alpha-diversity", filtered)
                .add_metadata("metadata-file", self._context.ctn_metadata)
                .add_output("visualization", filtered.replace(".qza", ".qzv"))
                .get_outputs()
            )
        # endregion

        # region Beta Diversity Analysis
        for key in "Species", "Location", "SampleGender":
            beta_visualized = (
                assembly.new_cmd("qiime diversity beta-group-significance")
                .add_option("quiet")
                .add_parameter("p-value-correction", "fdr")
                .add_parameter("pairwise", "--p-pairwise")
                .add_metadata("metadata-file", self._context.ctn_metadata)
                .add_metadata("metadata-column", key)
                .add_input(
                    "distance-matrix", core_dir / "weighted_unifrac_distance_matrix.qza"
                )
                .add_output("visualization", beta_dir / f"weighted_unifrac-{key}.qzv")
                .get_outputs()
            )
        # endregion

        # region Taxonomy
        taxonomy_visualized = (
            assembly.new_cmd("qiime taxa barplot")
            .add_option("quiet")
            .add_input("table", bio_free_table)
            .add_input("taxonomy", bio_free_classfied)
            .add_metadata("metadata-file", self._context.ctn_metadata)
            .add_output("visualization", output / "taxa-bar-plots.qzv")
            .get_outputs()
        )
        # endregion

        # fmt: on

        assembly.sort_commands()
        return assembly, requires
