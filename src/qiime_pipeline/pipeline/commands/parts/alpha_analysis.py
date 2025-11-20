from qiime_pipeline.pipeline import support


class alpha_analysis(support.Pipeline):
    def _cmd_build(self, inputs: dict[str] = None) -> dict[str]:
        super()._cmd_build(inputs)

        for index_file_name in [
            "faith_pd_vector",
            "observed_features_vector",
            "shannon_vector",
        ]:
            filtered = (
                self._assembly.new_cmd("qiime diversity filter-alpha-diversity")
                .add_input("alpha-diversity", inputs[index_file_name])
                .add_metadata("metadata-file", self._context.ctn_metadata)
                .add_output(
                    "filtered-alpha-diversity",
                    self._output / f"filtered_{index_file_name}.qza",
                )
                .get_outputs()
            )

            alpha_visualized = (
                self._assembly.new_cmd("qiime diversity alpha-group-significance")
                .add_input("alpha-diversity", filtered)
                .add_metadata("metadata-file", self._context.ctn_metadata)
                .add_output("visualization", filtered.replace(".qza", ".qzv"))
                .get_outputs()
            )

            self._result[f"filtered_{index_file_name}"] = filtered
            self._result[f"visualized_alpha_{index_file_name}"] = alpha_visualized

        return {**inputs, **self._result}
