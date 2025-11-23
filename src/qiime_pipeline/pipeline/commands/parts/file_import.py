from qiime_pipeline.pipeline import support


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

        denoised_table, denoised_seq, denoised_stats, base_transition = (
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
            .add_output("base-transition-stats", self._output / "base-transition-stats.qza")
            .get_outputs()
        )

        self._result["imported"] = imported
        self._result["denoised_table"] = denoised_table
        self._result["denoised_seq"] = denoised_seq
        self._result["denoised_stats"] = denoised_stats
        self._result["base_transition"] = base_transition

        return self._result
