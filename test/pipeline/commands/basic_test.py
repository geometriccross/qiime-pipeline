from pathlib import PurePath
from src.pipeline.commands import (
    file_import,
    filtering,
    classified,
    remove_biology,
    phylogeny,
    core_metrics,
    taxonomy,
    alpha_analysis,
    beta_analysis,
)
from src.pipeline.main.util import copy_from_container


def test_run_rarefaction(testing_context):
    context = testing_context("BASIC_TEST_DATA").__next__()
    total_pipeline = (
        file_import(context)
        + filtering(context)
        + classified(context)
        + remove_biology(context)
        + phylogeny(context)
        + core_metrics(context)
        + taxonomy(context)
        + alpha_analysis(context)
        + beta_analysis(context)
    )

    pipeline_result = total_pipeline()
    assert len(pipeline_result) == 24

    total_pipeline.run()

    for value in pipeline_result.values():
        local_path = copy_from_container(
            context,
            PurePath(value),
        )

        assert local_path.exists()
        assert local_path.is_file()
