import pytest
import docker
from pathlib import Path
from tempfile import NamedTemporaryFile
from tomlkit.toml_file import TOMLFile
from scripts.executor import Executor
from scripts.data_store.dataset import Databank


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
