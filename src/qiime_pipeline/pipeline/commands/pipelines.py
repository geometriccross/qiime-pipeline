from . import parts


def pipeline_run(context, cmd_parts: list):
    first_one = cmd_parts[0](context)
    pipeline = sum(map(lambda part: part(context), cmd_parts[1:]), first_one)
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


def pipeline_ancom(context):
    cmds = [
        parts.file_import,
        parts.filtering,
        parts.classified,
        parts.remove_biology,
        parts.phylogeny,
        parts.core_metrics,
        parts.taxa_collapse,
        parts.ancombc,
        lambda context: parts.adonis(
            context, beta_index="unweighted_unifrac_distance_matrix"
        ),
        lambda context: parts.adonis(
            context, beta_index="weighted_unifrac_distance_matrix"
        ),
    ]

    return pipeline_run(context, cmds)
