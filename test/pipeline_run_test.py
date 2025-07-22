import pytest
import docker
from pathlib import Path
from tempfile import NamedTemporaryFile
from tomlkit.toml_file import TOMLFile
from scripts.pipeline_run import loading_data
from scripts.executor import Executor
from scripts.data_control.dataset import Databank


@pytest.fixture(scope="module")
def provid_executor():
    docker_client = docker.from_env()
    pipeline_img, _ = docker_client.images.build(
        path=".",
        dockerfile="Dockerfile",
        tag="qiime",
    )
    pipeline_ctn = docker_client.containers.run(
        pipeline_img, detach=True, remove=False, name="qiime_container"
    )

    with Executor(pipeline_ctn) as executor:
        yield executor


# fastqが配置されたcontainerを用意する必要があるため、このテストは一時的にコメントアウト
# def test_data_specification_is_json_is_not_exists():
# databank = data_specification(None)
# assert isinstance(databank, Databank)
# assert len(databank.sets) == 1  # Since we wrote an empty JSON
#


def test_loading_data_if_setting_file_exists(temporary_dataset):
    before_conversion = Databank(sets=[temporary_dataset])
    toml_doc = before_conversion.to_toml()
    with NamedTemporaryFile(delete=True) as tmp_file:
        toml_file = TOMLFile(tmp_file.name)
        toml_file.write(toml_doc)

        after_conversion = loading_data(Path(tmp_file.name))
        assert isinstance(after_conversion, Databank)
        assert len(after_conversion.sets) == 1  # Since we wrote an empty TOML
        assert after_conversion.sets.pop() == temporary_dataset
