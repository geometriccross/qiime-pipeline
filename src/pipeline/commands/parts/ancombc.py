from src.pipeline import support


class ancombc(support.Pipeline):
    def __init__(self, context, ctn_output=None, formula: str = "Species"):
        super().__init__(context, ctn_output)
        self.__formula = formula

    def _cmd_build(self, inputs=None) -> dict[str]:
        ancombc = (
            self._assembly.new_cmd("qiime composition ancombc")
            .add_input("i-table", inputs["collapsed_table"])
            .add_input("m-metadata-file", self._context.ctn_metadata)
            .add_parameter("p-formula", self.__formula)
            .add_parameter("p-prv-cut", 0.1)
            .add_output("o-differentials", self._output / "ancombc.qza")
            .get_outputs()
        )

        da_barplot = (
            self._assembly.new_cmd("qiime composition da-barplot")
            .add_input("i-data", ancombc)
            .add_parameter("p-label-limit", 2000)
            .add_parameter("p-significance-threshold", 0.01)
            .add_output("o-visualization", self._output / "da_barplot.qzv")
            .get_outputs()
        )

        self._result["ancombc"] = ancombc
        self._result["da_barplot"] = da_barplot

        return {**inputs, **self._result}
