from scripts.pipeline.commands.alpha_rarefaction import alpha_rarefaction_pipeline
from scripts.pipeline.main.util import copy_from_container


def test_command_list_check_current(mocked_context):
    alpha_rarefaction_pipeline(mocked_context).command_list()


def test_run_rarefaction(testing_context):
    context = testing_context("ALPHA_RAREFACTION_TEST_DATA").__next__()
    alpha_rarefaction = alpha_rarefaction_pipeline(context)
    alpha_rarefaction.run()

    output = copy_from_container(
        context, context.setting.container_data.output_path.ctn_pos
    )

    assert (output / "alpha_rarefaction.qzv").exists()
    assert (output / "denoised_stats.qza").exists()
    assert (output / "denoised_seq.qza").exists()
    assert (output / "denoised_table.qza").exists()
    assert (output / "paired_end_demux.qza").exists()
    assert (output / "rooted-tree.qza").exists()
    assert (output / "unrooted-tree.qza").exists()
    assert (output / "masked-aligned-rep-seqs.qza").exists()
    assert (output / "aligned-rep-seqs.qza").exists()
