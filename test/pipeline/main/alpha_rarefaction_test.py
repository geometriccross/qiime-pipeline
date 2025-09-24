import pytest
from scripts.pipeline.main.setup import setup_context
from scripts.pipeline.main.alpha_rarefaction import command_list


@pytest.fixture
def alpha_rare_context(namespace):
    context = setup_context(namespace)
    context.setting.sampling_depth = 4

    yield context

    try:
        context.executor.stop()
    except Exception as e:
        raise e


def test_command_list_check_current(mocked_context):
    assembly, result = command_list(mocked_context)
