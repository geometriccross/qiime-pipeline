import pytest
from scripts.pipeline.main.setup import setup_context
from scripts.pipeline.main.alpha_rarefaction import run_rarefaction, command_list


@pytest.fixture
def alpha_rare_context(namespace):
    context = setup_context(namespace)
    context.setting.sampling_depth = 4

    yield context

    try:
        context.executor.stop()
    except Exception as e:
        raise e


def test_command_list_check_current(alpha_rare_context):
    context = alpha_rare_context
    out_dir = context.setting.container_data.workspace_path
    base_dir = out_dir
    assembly = command_list(context, base_dir, out_dir)

    assembly.sort_commands()


@pytest.mark.slow
def test_run_rarefaction(alpha_rare_context):
    ctn_output_file = run_rarefaction(alpha_rare_context)
    files = alpha_rare_context.executor.run(["ls"]).split()
    assert (
        ctn_output_file.name in files
    ), f"File {ctn_output_file} does not exist in the container."
