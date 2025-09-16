import pytest
from scripts.pipeline.main.setup import setup_context
from scripts.pipeline.main.alpha_rarefaction import (
    run_rarefaction,
)


@pytest.mark.pipeline
def test_run_rarefaction(namespace):
    context = setup_context(namespace)

    ctn_output_file = run_rarefaction(context)
    stdout, stderr = context.executor.run(["test", "-f", str(ctn_output_file)])
    assert stderr == ""

    context.executor.__container.stop()
