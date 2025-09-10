from scripts.pipeline.main.setup import setup_context
from scripts.pipeline.main.sampling_and_rarefaction import (
    run_rarefaction,
)


def test_run_rarefaction(namespace):
    context = setup_context(namespace)
    run_rarefaction(context)
