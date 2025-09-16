import pytest
from scripts.pipeline.main.setup import setup_context
from scripts.pipeline.main.alpha_rarefaction import (
    run_rarefaction,
)


@pytest.fixture
def alpha_rare_context(namespace):
    context = setup_context(namespace)
    context.setting.sampling_depth = 4

    yield context

    try:
        context.executor.__container.stop()
    except Exception as e:
        raise e


@pytest.mark.pipeline
def test_run_rarefaction(alpha_rare_context):
    ctn_output_file = run_rarefaction(alpha_rare_context)
    files = alpha_rare_context.executor.run(["ls"]).split()
    assert (
        ctn_output_file.name in files
    ), f"File {ctn_output_file} does not exist in the container."
