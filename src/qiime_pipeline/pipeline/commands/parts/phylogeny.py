from src.pipeline import support


class phylogeny(support.Pipeline):
    def _cmd_build(self, inputs: dict[str] = None) -> dict[str]:
        super()._cmd_build(inputs)
        align_seq, masked_align_seq, unrooted_tree, rooted_tree = (
            self._assembly.new_cmd("qiime phylogeny align-to-tree-mafft-fasttree")
            .add_option("quiet")
            .add_input("sequences", inputs["bio_free_seq"])
            .add_output("alignment", self._output / "biology_free_aligned_rep_seqs.qza")
            .add_output(
                "masked-alignment",
                self._output / "biology_free_masked_aligned_rep_seqs.qza",
            )
            .add_output("tree", self._output / "biology_free_unrooted_tree.qza")
            .add_output("rooted-tree", self._output / "biology_free_rooted_tree.qza")
            .get_outputs()
        )

        self._result["bio_free_align_seq"] = align_seq
        self._result["bio_free_masked_align_seq"] = masked_align_seq
        self._result["bio_free_unrooted_tree"] = unrooted_tree
        self._result["bio_free_rooted_tree"] = rooted_tree

        return {**inputs, **self._result}
