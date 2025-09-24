from scripts.pipeline.main.alpha_rarefaction import alpha_rarefaction_pipeline
from scripts.pipeline.main.db import db_pipeline
from scripts.pipeline.main.basic import basic_pipeline
from scripts.pipeline.main.alpha import alpha_analysis_pipeline
from scripts.pipeline.main.beta import beta_analysis_pipeline
from scripts.pipeline.main.taxonomy import taxonomy_pipeline


def test_alpha_rarefaction_commands_is_current(mocked_context):
    assembly, dirs, result = alpha_rarefaction_pipeline(mocked_context).command_list()


def test_db_commands_is_current(mocked_context):
    assembly, dirs, result = db_pipeline(mocked_context).command_list()


def test_basic_commands_is_current(mocked_context):
    assembly, dirs, classified, coremetrics = basic_pipeline(
        mocked_context
    ).command_list()


def test_alpha_commands_is_current(mocked_context, tmp_path):
    observed = str(tmp_path / "observed.qza")
    shannon = str(tmp_path / "shannon.qza")
    faith_pd = str(tmp_path / "faith_pd.qza")
    assembly, dirs, result = alpha_analysis_pipeline(mocked_context).command_list(
        observed, shannon, faith_pd
    )

    assert len(result) == 3
    assert result[0].endswith("filtered_observed.qzv")
    assert result[1].endswith("filtered_shannon.qzv")
    assert result[2].endswith("filtered_faith_pd.qzv")


def test_beta_commands_is_current(mocked_context, tmp_path):
    weighted_unifrac = str(tmp_path / "weighted_unifrac.qza")
    assembly, dirs, result = beta_analysis_pipeline(mocked_context).command_list(
        weighted_unifrac
    )

    assert len(result) == 3
    assert result[0].endswith("weighted_unifrac-Species.qzv")
    assert result[1].endswith("weighted_unifrac-Location.qzv")
    assert result[2].endswith("weighted_unifrac-SampleGender.qzv")


def test_taxonomy_commands_is_current(mocked_context, tmp_path):
    table = str(tmp_path / "table.qza")
    classifier = str(tmp_path / "classifier.qza")
    assembly, dirs, result = taxonomy_pipeline(mocked_context).command_list(
        table, classifier
    )

    assert len(result) == 1
    assert result[0].endswith("taxa-bar-plots.qzv")
