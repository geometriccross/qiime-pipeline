from pathlib import PurePath
from src.pipeline.commands.alpha_rarefaction import (
    file_import,
    alpha_rarefaction,
)
from src.pipeline.main.util import copy_from_container


def test_alpha_rarefaction_run(testing_context, tmp_path):
    context = testing_context("ALPHA_RAREFACTION_TEST_DATA").__next__()
    context.setting.container_data.output_path.ctn_pos = tmp_path

    file_import_ins = file_import(context)
    alpha_rarefaction_ins = alpha_rarefaction(context)

    concatinate = file_import_ins + alpha_rarefaction_ins
    pipeline_result = concatinate()
    concatinate.run()

    for value in pipeline_result.values():
        local_path = copy_from_container(
            context,
            PurePath(value),
        )

        assert local_path.exists()
        assert local_path.is_file()
