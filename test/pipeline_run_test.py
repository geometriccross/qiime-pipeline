import pytest
import docker
from pathlib import Path
from tempfile import NamedTemporaryFile
from scripts.pipeline_run import data_specification
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


def test_data_specification_is_json_exists(temporary_dataset):
    with NamedTemporaryFile(delete=True) as tmp_json:
        json_data = '{"sets": [' + temporary_dataset.to_json() + "]}"
        tmp_json.write(json_data.encode("utf-8"))
        tmp_json.flush()
        databank = data_specification(Path(tmp_json.name))
        assert isinstance(databank, Databank)
        assert len(databank.sets) == 1  # Since we wrote an empty JSON
