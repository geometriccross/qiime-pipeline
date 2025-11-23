from qiime_pipeline.pipeline import support


class beta_analysis(support.Pipeline):
    def _cmd_build(self, inputs: dict[str] = None, *target_keys) -> dict[str]:
        super()._cmd_build(inputs)

        if self._context.get_sampling_depth() < 10:
            # テスト用データは数が少ないため、ここはスキップする
            # 通常のデータではまず通るはず
            return {**inputs, **self._result}

        if target_keys is None or len(target_keys) == 0:
            target_keys = ["Host", "Species"]

        for key in target_keys:
            for index_file_name in [
                "unweighted_unifrac_distance_matrix",
                "weighted_unifrac_distance_matrix",
                "jaccard_distance_matrix",
                "bray_curtis_distance_matrix",
            ]:
                beta_visualized = (
                    self._assembly.new_cmd("qiime diversity beta-group-significance")
                    .add_parameter("pairwise", True)
                    .add_metadata("metadata-file", self._context.paths.metadata)
                    .add_metadata("metadata-column", f"{key}")
                    .add_input("distance-matrix", inputs[index_file_name])
                    .add_output(
                        "visualization", self._output / f"visualized_beta_{key}.qzv"
                    )
                    .get_outputs()
                )

                self._result[f"visualized_{index_file_name}_{key}"] = beta_visualized

        return {**inputs, **self._result}
