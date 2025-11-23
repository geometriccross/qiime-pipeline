from qiime_pipeline.pipeline import support


class ancombc(support.Pipeline):
    def __init__(self, context, ctn_output=None, formula: str = "Species"):
        super().__init__(context, ctn_output)
        self.__formula = formula

    def _cmd_build(self, inputs=None) -> dict[str]:
        ancombc = (
            self._assembly.new_cmd("qiime composition ancombc")
            .add_input("table", inputs["collapsed_table"])
            .add_metadata("metadata-file", self._context.paths.metadata)
            .add_parameter("formula", self.__formula)
            .add_parameter("prv-cut", 0.1)
            .add_output("differentials", self._output / "ancombc.qza")
            .get_outputs()
        )

        da_barplot = (
            self._assembly.new_cmd("qiime composition da-barplot")
            .add_input("data", ancombc)
            .add_parameter("label-limit", 2000)
            .add_parameter("significance-threshold", 0.01)
            .add_output(
                "visualization", self._output / f"da_barplot_{self.__formula}.qzv"
            )
            .get_outputs()
        )

        self._result["ancombc"] = ancombc
        self._result[f"da_barplot_{self.__formula}"] = da_barplot

        return {**inputs, **self._result}
