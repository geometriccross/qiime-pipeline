from src.pipeline import support


class taxa_collapse(support.Pipeline):
    def _cmd_build(self, inputs: dict[str] = None) -> dict[str]:
        super()._cmd_build(inputs)

        collapsed_table = (
            self._assembly.new_cmd("qiime taxa collapse")
            .add_input("table", inputs["filtered_table"])
            .add_input("taxonomy", inputs["classfied"])
            .add_parameter("level", 6)
            .add_output("collapsed-table", self._output / "collapsed_table_6.qza")
            .get_outputs()
        )

        self._result["collapsed_table"] = collapsed_table

        return {**inputs, **self._result}
