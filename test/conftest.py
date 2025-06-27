import pytest
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from scripts.data_control.dataset import Dataset


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
    )
    yield dataset
