import pytest
import docker
from scripts.executor import Executor


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


def test_run():
    from scripts.pipeline_run import pipeline_run, setup_databank
    from argparse import Namespace

    # Mock arguments
    args = Namespace(
        dockerfile="Dockerfile",
        sampling_depth=10000,
        data=[("metadata.tsv", "fastq_folder")],
        workspace_path="/workspace",
    )

    setting_data = setup_databank(args)

    # Run the pipeline
    pipeline_run(setting_data)

    # Check if the container is running
    assert docker.containers.get("qiime_container").status == "running"
