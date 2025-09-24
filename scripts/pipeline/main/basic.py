#!/usr/bin/env python
# flake8: noqa

from scripts.pipeline import support


class basic_pipeline(support.Pipeline):
    def __init__(self, context: support.PipelineContext):
        self.__context = context

    def command_list(self) -> tuple[support.Q2CmdAssembly, str, str]:
        output = self.__context.setting.container_data.output_path.ctn_pos
        assembly = support.Q2CmdAssembly()

        pre_dir = output / "pre"
        core_dir = output / "core"

        db_path = self.__context.setting.container_data.database_path.ctn_pos

        # fmt: off

        imported = (
            assembly.new_cmd("qiime tools import")
            .add_option("type", "SampleData[PairedEndSequencesWithQuality]")
            .add_option("input-format", "PairedEndFastqManifestPhred33V2")
            .add_option("input-path", self.__context.ctn_manifest)
            .add_option("output-path", pre_dir / "paired_end_demux.qza")
            .get_outputs()
        )

        dataset = next(iter(self.__context.setting.datasets.sets))
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

        sampling_depth = self.__context.setting.sampling_depth

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
            .add_output("alignment", output / "common_biology_free_aligned-rep-seqs.qza")
            .add_output("masked-alignment", output / "common_biology_free_masked-aligned-rep-seqs.qza")
            .add_output("tree", output / "common_biology_free_unrooted-tree.qza")
            .add_output("rooted-tree", output / "common_biology_free_rooted-tree.qza")
            .get_outputs()
        )

        bio_free_classfied = (
            assembly.new_cmd("qiime feature-classifier classify-sklearn")
            .add_option("quiet")
            .add_input("classifier", db_path)
            .add_input("reads", bio_free_seq)
            .add_output("classification", output / "common_biology_free_classification.qza")
            .get_outputs()
        )

        core_metrics_dir = (
            assembly.new_cmd("qiime diversity core-metrics-phylogenetic")
            .add_option("quiet")
            .add_input("phylogeny", rooted_tree)
            .add_input("table", bio_free_table)
            .add_metadata("metadata-file", self.__context.ctn_metadata)
            .add_parameter("sampling-depth", str(sampling_depth))
            .add_output("output-dir", core_dir)
            .get_outputs()
        )

        # fmt: on

        assembly.sort_commands()
        return assembly, core_metrics_dir, bio_free_classfied
