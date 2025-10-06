import pytest
from pathlib import Path
from argparse import Namespace
from src.pipeline.main.setup import setup_context


@pytest.fixture
def mocked_context(namespace, mocker):
    # setup_executorの戻り値をモック化
    mock_executor = mocker.Mock()
    mocker.patch("src.pipeline.main.setup.setup_executor", return_value=mock_executor)

    context = setup_context(namespace)
    context.setting.sampling_depth = 4

    return context


@pytest.fixture
def testing_context(tmp_path, data_path_pairs) -> Namespace:
    def _testing_context(gdrive_env_var):
        namespace = Namespace(
            pipeline="basic",
            data=data_path_pairs(gdrive_env_var),
            dataset_region="V3V4",
            image="quay.io/qiime2/amplicon:latest",
            dockerfile=Path("dockerfiles/Dockerfile"),
            local_output=Path(tmp_path / "output"),
            local_database=Path("db/classifier.qza"),
            sampling_depth=5,  # 非常に低い値がテストのシグナルとなる。この値が10以下かどうかでパイプラインはテストが行われているかを判断する
        )

        context = setup_context(namespace)

        try:
            yield context
            context.executor.stop()
        except Exception as e:
            raise e

    return _testing_context
