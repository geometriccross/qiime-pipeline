from qiime_pipeline.pipeline import support


class core_metrics(support.Pipeline):
    def _cmd_build(self, inputs: dict[str] = None) -> dict[str]:
        super()._cmd_build(inputs)
        sampling_depth = self._context.get_sampling_depth()

        def add_suffix(name: str, suffix: str = "qza") -> str:
            return self._output / f"{name}.{suffix}"

        output_file_keys = [
            rarefied_table := "rarefied_table",
            faith_pd_vector := "faith_pd_vector",
            observed_features_vector := "observed_features_vector",
            shannon_vector := "shannon_vector",
            evenness_vector := "evenness_vector",
            unweighted_unifrac_distance_matrix := "unweighted_unifrac_distance_matrix",
            weighted_unifrac_distance_matrix := "weighted_unifrac_distance_matrix",
            jaccard_distance_matrix := "jaccard_distance_matrix",
            bray_curtis_distance_matrix := "bray_curtis_distance_matrix",
            unweighted_unifrac_pcoa_results := "unweighted_unifrac_pcoa_results",
            weighted_unifrac_pcoa_results := "weighted_unifrac_pcoa_results",
            jaccard_pcoa_results := "jaccard_pcoa_results",
            bray_curtis_pcoa_results := "bray_curtis_pcoa_results",
            unweighted_unifrac_emperor := "unweighted_unifrac_emperor",
            weighted_unifrac_emperor := "weighted_unifrac_emperor",
            jaccard_emperor := "jaccard_emperor",
            bray_curtis_emperor := "bray_curtis_emperor",
        ]

        core_metrics_files = (
            self._assembly.new_cmd("qiime diversity core-metrics-phylogenetic")
            .add_option("quiet")
            .add_input("phylogeny", inputs["bio_free_rooted_tree"])
            .add_input("table", inputs["bio_free_table"])
            .add_metadata("metadata-file", self._context.paths.metadata)
            .add_parameter("sampling-depth", str(sampling_depth))
            .add_output("rarefied-table", add_suffix(rarefied_table))
            .add_output("faith-pd-vector", add_suffix(faith_pd_vector))
            .add_output(
                "observed-features-vector", add_suffix(observed_features_vector)
            )
            .add_output("shannon-vector", add_suffix(shannon_vector))
            .add_output("evenness-vector", add_suffix(evenness_vector))
            .add_output(
                "unweighted-unifrac-distance-matrix",
                add_suffix(unweighted_unifrac_distance_matrix),
            )
            .add_output(
                "weighted-unifrac-distance-matrix",
                add_suffix(weighted_unifrac_distance_matrix),
            )
            .add_output("jaccard-distance-matrix", add_suffix(jaccard_distance_matrix))
            .add_output(
                "bray-curtis-distance-matrix", add_suffix(bray_curtis_distance_matrix)
            )
            .add_output(
                "unweighted-unifrac-pcoa-results",
                add_suffix(unweighted_unifrac_pcoa_results),
            )
            .add_output(
                "weighted-unifrac-pcoa-results",
                add_suffix(weighted_unifrac_pcoa_results),
            )
            .add_output("jaccard-pcoa-results", add_suffix(jaccard_pcoa_results))
            .add_output(
                "bray-curtis-pcoa-results", add_suffix(bray_curtis_pcoa_results)
            )
            .add_output(
                "unweighted-unifrac-emperor",
                add_suffix(unweighted_unifrac_emperor, "qzv"),
            )
            .add_output(
                "weighted-unifrac-emperor", add_suffix(weighted_unifrac_emperor, "qzv")
            )
            .add_output("jaccard-emperor", add_suffix(jaccard_emperor, "qzv"))
            .add_output("bray-curtis-emperor", add_suffix(bray_curtis_emperor, "qzv"))
            .get_outputs()
        )

        for key, file_name in zip(output_file_keys, core_metrics_files):
            if key in file_name:
                self._result[key] = file_name
            else:
                raise ValueError(f"キーとファイル名が一致しません: {key} / {file_name}")

        return {**inputs, **self._result}
