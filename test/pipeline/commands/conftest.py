import pytest
from scripts.pipeline.main.setup import setup_context


@pytest.fixture
def mocked_context(namespace, mocker):
    # setup_executorの戻り値をモック化
    mock_executor = mocker.Mock()
    mocker.patch(
        "scripts.pipeline.main.setup.setup_executor", return_value=mock_executor
    )

    context = setup_context(namespace)
    context.setting.sampling_depth = 4

    return context
