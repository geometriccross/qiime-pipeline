from scripts.pipeline.commands import basic_pipeline
from scripts.pipeline.main.util import copy_from_container


def test_command_list_check_current(mocked_context):
    basic_pipeline(mocked_context).command_list()


def test_run_rarefaction(testing_context):
    context = testing_context("BASIC_TEST_DATA").__next__()
    alpha_rarefaction = basic_pipeline(context)
    alpha_rarefaction.run()

    output = copy_from_container(
        context, context.setting.container_data.output_path.ctn_pos
    )

    assert (output / "pre/denoised_stats.qza").exists()
    assert (output / "pre/denoised_seq.qza").exists()
    assert (output / "pre/denoised_table.qza").exists()
    assert (output / "pre/paired_end_demux.qza").exists()
