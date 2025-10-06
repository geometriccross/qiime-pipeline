from pathlib import PurePath
from src.pipeline.support.support_class import Pipeline
from src.pipeline.commands import parts


def test_pipeline_concatination_pipeline(mocked_context):
    file_import_ins = parts.file_import(mocked_context)
    alpha_rarefaction_ins = parts.alpha_rarefaction(mocked_context)
    filtering_ins = parts.filtering(mocked_context)

    concatinate = file_import_ins + alpha_rarefaction_ins + filtering_ins
    assert isinstance(concatinate, Pipeline)

    pipeline_exp_result = concatinate()
    assert len(pipeline_exp_result) == 11

    for value in pipeline_exp_result.values():
        assert value.endswith(".qza") or value.endswith(".qzv")
        assert PurePath(value).is_absolute()
