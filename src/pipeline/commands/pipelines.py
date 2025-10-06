from . import parts


def pipeline_run(context, cmd_parts: list):
    pipeline = sum(map(lambda part: part(context), cmd_parts))
    return pipeline.run()


def pipeline_alpha_rarefaction(context):
    return pipeline_run(
        context,
        [
            parts.file_import,
            parts.alpha_rarefaction,
        ],
    )


def pipeline_db(context):
    return pipeline_run(
        context,
        [parts.file_import, parts.db_generate],
    )


def pipeline_basic(context):
    return pipeline_run(
        context,
        [
            parts.file_import,
            parts.filtering,
            parts.classified,
            parts.remove_biology,
            parts.phylogeny,
            parts.core_metrics,
            parts.taxonomy,
            parts.alpha_analysis,
            parts.beta_analysis,
        ],
    )
