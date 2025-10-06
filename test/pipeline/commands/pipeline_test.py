from pathlib import PurePath
import pytest
from src.pipeline.commands import pipelines
from src.pipeline.main.util import copy_from_container


@pytest.mark.slow()
@pytest.mark.parametrize(
    "gdrive_env,target_func,expected_file_count",
    [
        ("ALPHA_RAREFACTION_TEST_DATA", pipelines.pipeline_alpha_rarefaction, 9),
        ("BASIC_TEST_DATA", pipelines.pipeline_basic, 38),
    ],
)
def test_pipeline_alpha_rarefaction(
    testing_context, tmp_path, gdrive_env, target_func, expected_file_count
):
    context = testing_context(gdrive_env).__next__()
    context.setting.container_data.output_path.ctn_pos = tmp_path

    result = target_func(context)

    for value in result.values():
        local_path = copy_from_container(
            context,
            PurePath(value),
        )

        assert local_path.exists()
        assert local_path.is_file()
