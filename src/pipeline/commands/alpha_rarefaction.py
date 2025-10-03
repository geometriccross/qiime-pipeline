#!/usr/bin/env python

from src.pipeline import support


class file_import(support.Pipeline):
    def _cmd_build(self, inputs: dict[str] = None) -> dict[str]:
        super()._cmd_build(inputs)

        imported = (
            self._assembly.new_cmd("qiime tools import")
            .add_option("type", "SampleData[PairedEndSequencesWithQuality]")
            .add_option("input-format", "PairedEndFastqManifestPhred33V2")
            .add_option("input-path", self._context.ctn_manifest)
            .add_option("output-path", self._output / "paired_end_demux.qza")
            .get_outputs()
        )

        # Get region settings from the first dataset
        dataset = next(iter(self._context.setting.datasets.sets))
        region = dataset.region

        denoised_table, denoised_seq, denoised_stats = (
            self._assembly.new_cmd("qiime dada2 denoise-paired")
            .add_option("quiet")
            .add_input("demultiplexed-seqs", imported)
            .add_parameter("n-threads", "0")
            .add_parameter("trim-left-f", str(region.trim_left_f))
            .add_parameter("trim-left-r", str(region.trim_left_r))
            .add_parameter("trunc-len-f", str(region.trunc_len_f))
            .add_parameter("trunc-len-r", str(region.trunc_len_r))
            .add_output("table", self._output / "denoised_table.qza")
            .add_output("representative-sequences", self._output / "denoised_seq.qza")
            .add_output("denoising-stats", self._output / "denoised_stats.qza")
            .get_outputs()
        )

        self._result["imported"] = imported
        self._result["denoised_table"] = denoised_table
        self._result["denoised_seq"] = denoised_seq
        self._result["denoised_stats"] = denoised_stats

        return self._result


class alpha_rarefaction(support.Pipeline):
    def _cmd_build(self, inputs: dict[str] = None) -> dict[str]:
        super()._cmd_build(inputs)
        # fmt: off

        align_seq, masked_align_seq, unrooted_tree, rooted_tree = (
            self._assembly.new_cmd("qiime phylogeny align-to-tree-mafft-fasttree")
            .add_option("quiet")
            .add_input("sequences", inputs["denoised_seq"])
            .add_output("alignment", self._output / "aligned-rep-seqs.qza")
            .add_output("masked-alignment", self._output / "masked-aligned-rep-seq.qza")
            .add_output("tree", self._output / "unrooted-tree.qza")
            .add_output("rooted-tree", self._output / "rooted-tree.qza")
            .get_outputs()
        )

        sampling_depth = self._context.setting.sampling_depth

        # 実行時のエラーを避けるため
        # steps, iterationsはサンプルのmax featureよりも十分に小さくする
        alpha_visualized = (
            self._assembly.new_cmd("qiime diversity alpha-rarefaction")
            .add_option("quiet")
            .add_input("table", inputs["denoised_table"])
            .add_input("phylogeny", rooted_tree)
            .add_parameter("min-depth", "1")
            .add_parameter("max-depth", sampling_depth)
            .add_parameter("steps", str(2) if sampling_depth < 10 else str(10))
            .add_parameter("iterations", str(1) if sampling_depth < 10 else str(10))
            .add_metadata("metadata-file", str(self._context.ctn_metadata))
            .add_output("visualization", self._output / "alpha_rarefaction.qzv")
            .get_outputs()
        )

        # fmt: on

        self._result["align_seq"] = align_seq
        self._result["masked_align_seq"] = masked_align_seq
        self._result["unrooted_tree"] = unrooted_tree
        self._result["rooted_tree"] = rooted_tree
        self._result["alpha_visualized"] = alpha_visualized

        return {**inputs, **self._result}
