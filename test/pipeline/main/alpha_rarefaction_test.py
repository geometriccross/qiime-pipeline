import pytest
from scripts.pipeline.main.setup import setup_context
from scripts.pipeline.main.alpha_rarefaction import (
    run_rarefaction,
)


@pytest.mark.slow
def test_run_rarefaction(namespace):
    context = setup_context(namespace)
    run_rarefaction(context)
