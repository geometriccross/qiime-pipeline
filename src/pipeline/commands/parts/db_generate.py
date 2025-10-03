import support


class db_generate(support.Pipeline):
    def _cmd_build(self, inputs=None):
        super()._cmd_build(inputs)

        silva_seq, silva_tax = (
            self._assembly.new_cmd("qiime rescript get-silva-data")
            .add_parameter("p-version", "138.2")
            .add_parameter("target", "SSURef_NR99")
            .add_output("silva-sequences", self._output / "silva-seqs.qza")
            .add_output("silva-taxonomy", self._output / "silva-tax.qza")
            .get_outputs()
        )

        silva_read = (
            self._assembly.new_cmd("qiime feature-classifier extract-reads")
            .add_input("sequences", silva_seq)
            .add_parameter("min-length", "350")
            .add_parameter("max-length", "500")
            .add_parameter("f-primer", "CCTACGGGNGGCWGCAG")
            .add_parameter("r-primer", "GACTACHVGGGTATCTAATCC")
            .add_output("reads", self._output / "silva-reads.qza")
            .get_outputs()
        )

        db = (
            self._assembly.new_cmd(
                "qiime feature-classifier fit-classifier-naive-bayes"
            )
            .add_input("reference-reads", silva_read)
            .add_input("reference-taxonomy", silva_tax)
            .add_output("classifier", self._output / "classifier-silva138.qza")
            .get_outputs()
        )

        self._result["silva_seq"] = silva_seq
        self._result["silva_tax"] = silva_tax
        self._result["silva_read"] = silva_read
        self._result["db"] = db

        self._assembly.sort_commands()
        return
