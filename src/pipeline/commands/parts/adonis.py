from src.pipeline import support


class adonis(support.Pipeline):
    def __init__(
        self,
        context,
        ctn_output=None,
        formula: str = "Species",
        beta_index: str = "unweighted_unifrac_distance_matrix",
    ):
        super().__init__(context, ctn_output)
        self.__formula = formula
        self.__beta_index = beta_index

    def _cmd_build(self, inputs: dict[str] = None) -> dict[str]:
        super()._cmd_build(inputs)

        adonis = (
            self._assembly.new_cmd("qiime diversity adonis")
            .add_input("i-distance-matrix", self.__beta_index)
            .add_input("m-metadata-file", self._context.ctn_metadata)
            .add_parameter("p-formula", self.__formula)
            .add_output(
                "o-visualization", self._output / f"adonis_{self.__beta_index}.qzv"
            )
            .get_outputs()
        )

        self._result[f"adonis_{self.__beta_index}"] = adonis

        return {**inputs, **self._result}
