from scripts.pipeline import support


class taxonomy_pipeline(support.Pipeline):
    def __init__(self, context: support.PipelineContext):
        self.__context = context

    def command_list(
        self, table: str, classifier: str
    ) -> tuple[support.Q2CmdAssembly, support.RequiresDirectory, list[str]]:
        output = self.__context.setting.container_data.output_path.ctn_pos

        requires = support.RequiresDirectory()
        requires.add(output)

        assembly = support.Q2CmdAssembly()
        visualized = []

        visualized.append(
            assembly.new_cmd("qiime taxa barplot")
            .add_option("quiet")
            .add_input("table", table)
            .add_input("taxonomy", classifier)
            .add_metadata("metadata-file", self.__context.ctn_metadata)
            .add_output("visualization", output / "taxa-bar-plots.qzv")
            .get_outputs()
        )

        return assembly, requires, visualized
