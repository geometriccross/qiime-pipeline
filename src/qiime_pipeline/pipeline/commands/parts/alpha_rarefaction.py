from qiime_pipeline.pipeline import support


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

        sampling_depth = self._context.get_sampling_depth()

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
            .add_metadata("metadata-file", str(self._context.paths.metadata))
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
