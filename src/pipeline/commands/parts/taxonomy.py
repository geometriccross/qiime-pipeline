from src.pipeline import support


class taxonomy(support.Pipeline):
    def _cmd_build(self, inputs: dict[str] = None) -> dict[str]:
        super()._cmd_build(inputs)

        taxonomy_barplot = (
            self._assembly.new_cmd("qiime taxa barplot")
            .add_option("quiet")
            .add_input("table", inputs["bio_free_table"])
            .add_input("taxonomy", inputs["bio_free_classfied"])
            .add_metadata("metadata-file", self._context.ctn_metadata)
            .add_output("visualization", self._output / "taxa-bar-plots.qzv")
            .get_outputs()
        )

        self._result["taxonomy_barplot"] = taxonomy_barplot

        return {**inputs, **self._result}
