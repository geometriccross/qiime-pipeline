from src.pipeline import support


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


class remove_biology(support.Pipeline):
    def _cmd_build(self, inputs: dict[str] = None) -> dict[str]:
        super()._cmd_build(inputs)
        db_path = self._context.setting.container_data.database_path.ctn_pos

        bio_free_seq = (
            self._assembly.new_cmd("qiime taxa filter-seqs")
            .add_option("quiet")
            .add_parameter("exclude", "mitochondria,cyanobacteria")
            .add_input("sequences", inputs["filtered_seq"])
            .add_input("taxonomy", inputs["classfied"])
            .add_output(
                "filtered-sequences", self._output / "common_biology_free_seq.qza"
            )
            .get_outputs()
        )

        bio_free_table = (
            self._assembly.new_cmd("qiime taxa filter-table")
            .add_option("quiet")
            .add_parameter("exclude", "mitochondria,cyanobacteria")
            .add_input("table", inputs["filtered_table"])
            .add_input("taxonomy", inputs["classfied"])
            .add_output(
                "filtered-table", self._output / "common_biology_free_table.qza"
            )
            .get_outputs()
        )

        bio_free_classfied = (
            self._assembly.new_cmd("qiime feature-classifier classify-sklearn")
            .add_option("quiet")
            .add_input("classifier", db_path)
            .add_input("reads", bio_free_seq)
            .add_output(
                "classification",
                self._output / "common_biology_free_classification.qza",
            )
            .get_outputs()
        )

        self._result["bio_free_seq"] = bio_free_seq
        self._result["bio_free_table"] = bio_free_table
        self._result["bio_free_classfied"] = bio_free_classfied

        return {**inputs, **self._result}


class phylogeny(support.Pipeline):
    def _cmd_build(self, inputs: dict[str] = None) -> dict[str]:
        super()._cmd_build(inputs)
        align_seq, masked_align_seq, unrooted_tree, rooted_tree = (
            self._assembly.new_cmd("qiime phylogeny align-to-tree-mafft-fasttree")
            .add_option("quiet")
            .add_input("sequences", inputs["bio_free_seq"])
            .add_output("alignment", self._output / "biology_free_aligned_rep_seqs.qza")
            .add_output(
                "masked-alignment",
                self._output / "biology_free_masked_aligned_rep_seqs.qza",
            )
            .add_output("tree", self._output / "biology_free_unrooted_tree.qza")
            .add_output("rooted-tree", self._output / "biology_free_rooted_tree.qza")
            .get_outputs()
        )

        self._result["bio_free_align_seq"] = align_seq
        self._result["bio_free_masked_align_seq"] = masked_align_seq
        self._result["bio_free_unrooted_tree"] = unrooted_tree
        self._result["bio_free_rooted_tree"] = rooted_tree

        return {**inputs, **self._result}


class core_metrics(support.Pipeline):
    def _cmd_build(self, inputs: dict[str] = None) -> dict[str]:
        super()._cmd_build(inputs)
        sampling_depth = self._context.setting.sampling_depth

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
            .add_metadata("metadata-file", self._context.ctn_metadata)
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


class alpha_analysis(support.Pipeline):
    def _cmd_build(self, inputs: dict[str] = None) -> dict[str]:
        super()._cmd_build(inputs)

        for index_file_name in [
            "observed_features_vector",
            "shannon_vector",
            "faith_pd_vector",
        ]:
            filtered = (
                self._assembly.new_cmd("qiime diversity filter-alpha-diversity")
                .add_input("alpha-diversity", index_file_name)
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


class beta_analysis(support.Pipeline):
    def _cmd_build(self, inputs: dict[str] = None, *target_keys) -> dict[str]:
        super()._cmd_build(inputs)

        if self._context.setting.sampling_depth < 10:
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
                    .add_metadata("metadata-file", self._context.ctn_metadata)
                    .add_metadata("metadata-column", f"{key}")
                    .add_input("distance-matrix", inputs[index_file_name])
                    .add_output(
                        "visualization", self._output / f"visualized_beta_{key}.qzv"
                    )
                    .get_outputs()
                )

                self._result[f"visualized_{index_file_name}_{key}"] = beta_visualized

        return {**inputs, **self._result}
