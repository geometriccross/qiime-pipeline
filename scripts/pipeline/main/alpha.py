#!/usr/bin/env python
# flake8: noqa

from scripts.pipeline import support


class alpha_analysis_pipeline(support.Pipeline):
    def __init__(self, context: support.PipelineContext):
        self.__context = context

    def command_list(
        self, observed: str, shannon: str, faith_pd: str
    ) -> tuple[support.Q2CmdAssembly, support.RequiresDirectory, list[str]]:
        output = self.__context.setting.container_data.output_path.ctn_pos
        alpha_dir = output / "alpha"

        requires = support.RequiresDirectory()
        requires.add(output)
        requires.add(alpha_dir)

        assembly = support.Q2CmdAssembly()
        visualized = []
        for name, alpha_index in [
            ("observed", observed),
            ("shannon", shannon),
            ("faith_pd", faith_pd),
        ]:
            # fmt: off
            
            filtered = (
                assembly.new_cmd("qiime diversity filter-alpha-diversity")
                .add_input("alpha-diversity", alpha_index)
                .add_metadata("metadata-file", self.__context.ctn_metadata)
                .add_output("filtered-alpha-diversity", alpha_dir / f"filtered_{name}.qza")
                .get_outputs()
            )

            visualized.append(
                assembly.new_cmd("qiime diversity alpha-group-significance")
                .add_input("alpha-diversity", filtered)
                .add_metadata("metadata-file", self.__context.ctn_metadata)
                .add_output("visualization", filtered.replace(".qza", ".qzv"))
                .get_outputs()
            )

            # fmt: on

        assembly.sort_commands()
        return assembly, requires, visualized
