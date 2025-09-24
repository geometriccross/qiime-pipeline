from scripts.pipeline import support


class beta_analysis_pipeline(support.Pipeline):
    def __init__(self, context: support.PipelineContext):
        self.__context = context

    def command_list(
        self, weighted_unifrac: str
    ) -> tuple[support.Q2CmdAssembly, support.RequiresDirectory, list[str]]:
        output = self.__context.setting.container_data.output_path.ctn_pos
        beta_dir = output / "beta"

        requires = support.RequiresDirectory()
        requires.add(output)
        requires.add(beta_dir)

        assembly = support.Q2CmdAssembly()
        visualized = []

        for key in "Species", "Location", "SampleGender":
            visualized.append(
                assembly.new_cmd("qiime diversity beta-group-significance")
                .add_option("quiet")
                .add_parameter("p-value-correction", "fdr")
                .add_parameter("pairwise", "--p-pairwise")
                .add_metadata("metadata-file", self.__context.ctn_metadata)
                .add_metadata("metadata-column", key)
                .add_input("distance-matrix", weighted_unifrac)
                .add_output("visualization", beta_dir / f"weighted_unifrac-{key}.qzv")
                .get_outputs()
            )

        return assembly, requires, visualized
