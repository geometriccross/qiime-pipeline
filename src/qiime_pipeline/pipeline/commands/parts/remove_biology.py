from qiime_pipeline.pipeline import support


class remove_biology(support.Pipeline):
    def _cmd_build(self, inputs: dict[str] = None) -> dict[str]:
        super()._cmd_build(inputs)
        db_path = self._context.get_database_path()

        bio_free_seq = (
            self._assembly.new_cmd("qiime taxa filter-seqs")
            .add_option("quiet")
            .add_parameter("exclude", "mitochondria,cyanobacteria")
            .add_input("sequences", inputs["filtered_seq"])
            .add_input("taxonomy", inputs["classfied"])
            .add_output(
                "filtered-sequences", self._output / "common_biology_free_seq.qza"
            )
            .get_outputs()
        )

        bio_free_table = (
            self._assembly.new_cmd("qiime taxa filter-table")
            .add_option("quiet")
            .add_parameter("exclude", "mitochondria,cyanobacteria")
            .add_input("table", inputs["filtered_table"])
            .add_input("taxonomy", inputs["classfied"])
            .add_output(
                "filtered-table", self._output / "common_biology_free_table.qza"
            )
            .get_outputs()
        )

        bio_free_classfied = (
            self._assembly.new_cmd("qiime feature-classifier classify-sklearn")
            .add_option("quiet")
            .add_input("classifier", db_path)
            .add_input("reads", bio_free_seq)
            .add_parameter("n-jobs", 2)
            .add_parameter("reads-per-batch", 2000)
            .add_output(
                "classification",
                self._output / "common_biology_free_classification.qza",
            )
            .get_outputs()
        )

        self._result["bio_free_seq"] = bio_free_seq
        self._result["bio_free_table"] = bio_free_table
        self._result["bio_free_classfied"] = bio_free_classfied

        return {**inputs, **self._result}
