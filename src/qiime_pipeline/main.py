#!/usr/bin/env python

from .pipeline import commands
from .pipeline.main.setup import setup
from .pipeline.main.util import copy_from_container
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

    _pipeline_func(context.pipeline_type)(context)
    copy_from_container(context, context.setting.ctn_output_path)
    context.executor.stop()


if __name__ == "__main__":
    main()
