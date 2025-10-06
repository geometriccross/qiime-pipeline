#!/usr/bin/env python

from .pipeline import commands
from .pipeline.main.setup import setup
from .pipeline.main.util import find, copy_from_container
from .pipeline.support import PipelineType


def _pipeline_func(pipeline_type: PipelineType) -> callable:
    match pipeline_type:
        case PipelineType.BASIC:
            return commands.pipelines.pipeline_basic
        case PipelineType.RAREFACTION_CURVE:
            return commands.pipelines.pipeline_alpha_rarefaction
        case PipelineType.ANCOM:
            return commands.pipelines.pipeline_ancom
        case _:
            raise ValueError(f"Unsupported pipeline type: {pipeline_type}")


def main():
    context = setup()

    try:
        _pipeline_func(context.pipeline_type)(context).run()
    finally:
        context.executor.stop()
        output = copy_from_container(
            context, context.setting.container_data.output_path.ctn_pos
        )

        print("Output:")
        for file in find(output.iterdir(), ["qzv", "qza"]):
            print(file)


if __name__ == "__main__":
    main()
