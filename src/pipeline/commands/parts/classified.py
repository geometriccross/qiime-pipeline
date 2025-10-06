from src.pipeline import support


class classified(support.Pipeline):
    def _cmd_build(self, inputs: dict[str] = None) -> dict[str]:
        super()._cmd_build(inputs)
        db_path = self._context.setting.container_data.database_path.ctn_pos

        classfied = (
            self._assembly.new_cmd("qiime feature-classifier classify-sklearn")
            .add_option("quiet")
            .add_input("classifier", db_path)
            .add_input("reads", inputs["filtered_seq"])
            .add_output("classification", self._output / "classification.qza")
            .get_outputs()
        )

        self._result["classfied"] = classfied

        return {**inputs, **self._result}
