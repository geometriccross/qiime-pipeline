#!/usr/bin/env python

from scripts.pipeline import commands
from scripts.pipeline.main.setup import setup
from scripts.pipeline.main.util import find, copy_from_container


if __name__ == "__main__":
    context = setup()

    basic_cmd_result = commands.basic_pipeline(context).command_list()
    (
        basic_cmd_assembly,
        basic_cmd_requires,
        bio_free_table,
        bio_free_classfied,
        core_metrics_files,
    ) = basic_cmd_result

    taxonomy_cmd_result = commands.taxonomy_pipeline(context).command_list(
        bio_free_table, bio_free_classfied
    )
    (
        taxonomy_cmd_assembly,
        taxonomy_cmd_requires,
        visualized,
    ) = taxonomy_cmd_result

    alpha_cmd_result = commands.alpha_analysis_pipeline(context).command_list(
        find("observed", core_metrics_files),
        find("shannon", core_metrics_files),
        find("faith", core_metrics_files),
    )
    (
        alpha_cmd_assembly,
        alpha_cmd_requires,
        visualized,
    ) = alpha_cmd_result

    beta_cmd_result = commands.beta_analysis_pipeline(context).command_list(
        find("weighted_unifrac")
    )
    (
        beta_cmd_assembly,
        beta_cmd_requires,
        visualized,
    ) = beta_cmd_result

    # 集計
    full_assembly = (
        basic_cmd_assembly
        + taxonomy_cmd_assembly
        + alpha_cmd_assembly
        + beta_cmd_assembly
    )

    all_requires_dir = (
        basic_cmd_requires
        + taxonomy_cmd_requires
        + alpha_cmd_requires
        + beta_cmd_requires
    )

    full_assembly.sort_commands()

    all_requires_dir.ensure(context.executor)
    [context.executor.run(cmd) for cmd in full_assembly.build_all()]

    # コンテナからホストへコピー
    copy_from_container(context, context.setting.container_data.output_path.ctn_pos)
