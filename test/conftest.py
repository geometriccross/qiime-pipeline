import pytest
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from python_on_whales import docker
from scripts.pipeline.support.executor import Provider
from scripts.data.store.dataset import Dataset
from scripts.data.store.ribosome_regions import Region


@pytest.fixture()
def temporay_files():
    with TemporaryDirectory() as fastq_dir:
        with NamedTemporaryFile(delete=True) as metadata_file:
            yield {"fastq": Path(fastq_dir), "meta": Path(metadata_file.name)}


@pytest.fixture()
def temporary_dataset(temporay_files):
    dataset = Dataset(
        name="test_dataset",
        fastq_folder=temporay_files["fastq"],
        metadata_path=temporay_files["meta"],
        region=Region("SampleRegion", 0, 0, 0, 0),
    )
    yield dataset


@pytest.fixture
def trusted_provider():
    provider = Provider(image="alpine", remove=True)

    yield provider

    docker.container.remove(provider.provide(), force=True)
