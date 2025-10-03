import support


class filtering(support.Pipeline):
    def _cmd_build(self, inputs: dict[str] = None) -> dict[str]:
        super()._cmd_build(inputs)
        sampling_depth = self._context.setting.sampling_depth

        filtered_table = (
            self._assembly.new_cmd("qiime feature-table filter-samples")
            .add_option("quiet")
            .add_input("table", inputs["denoised_table"])
            .add_parameter("min-frequency", str(sampling_depth))
            .add_output("filtered-table", self._output / "filtered_table.qza")
            .get_outputs()
        )

        filtered_seq = (
            self._assembly.new_cmd("qiime feature-table filter-seqs")
            .add_option("quiet")
            .add_input("data", inputs["denoised_seq"])
            .add_input("table", filtered_table)
            .add_output("filtered-data", self._output / "filtered_seq.qza")
            .get_outputs()
        )

        self._result["filtered_table"] = filtered_table
        self._result["filtered_seq"] = filtered_seq

        return {**inputs, **self._result}
