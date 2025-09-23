import pytest
from scripts.pipeline.main.setup import setup_context
from scripts.pipeline.main.db import run_setup_database


@pytest.mark.slow
def test_run_setup_database(namespace):
    context = setup_context(namespace)
    ctn_output_file = run_setup_database(context)
    files = context.executor.run(["ls"]).split()
    assert (
        ctn_output_file.name in files
    ), f"File {ctn_output_file} does not exist in the container."
