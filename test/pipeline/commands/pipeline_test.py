from pathlib import PurePath
import pytest
from src.pipeline.commands import pipelines
from src.pipeline.main.util import copy_from_container


@pytest.mark.slow
@pytest.mark.parametrize(
    "gdrive_env,target_func,expected_file_count",
    [
        ("ALPHA_RAREFACTION_TEST_DATA", pipelines.pipeline_alpha_rarefaction, 9),
        ("BASIC_TEST_DATA", pipelines.pipeline_basic, 38),
        ("BASIC_TEST_DATA", pipelines.pipeline_ancom, 38),
    ],
)
def test_pipeline(testing_context, gdrive_env, target_func, expected_file_count):
    context = testing_context(gdrive_env).__next__()

    result = target_func(context)

    for value in result.values():
        local_path = copy_from_container(
            context,
            PurePath(value),
        )

        assert local_path.exists()
        assert local_path.is_file()
