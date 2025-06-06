import pytest
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from scripts.data_control.dataset import Dataset, Databank


@pytest.fixture()
def temporay_files():
    with TemporaryDirectory() as fastq_dir:
        with NamedTemporaryFile(delete=True) as metadata_file:
            yield {"fastq": Path(fastq_dir), "meta": Path(metadata_file.name)}


def test_dataset_raise_error_when_specify_incorrect_path(temporay_files):
    def check(fastq_folder, metadata_path, err_msg):
        try:
            Dataset(
                name="test_dataset",
                fastq_folder=fastq_folder,
                metadata_path=metadata_path,
            )
        except FileNotFoundError as e:
            assert str(e) == err_msg

    check(
        fastq_folder=Path("non_existent.fastq"),
        metadata_path=Path("non_existent_metadata.tsv"),
        err_msg="Fastq path non_existent.fastq does not exist.",
    )

    check(
        fastq_folder=Path(temporay_files["fastq"]),
        metadata_path=Path("non_existent_metadata.tsv"),
        err_msg="Metadata path non_existent_metadata.tsv does not exist.",
    )

    assert Dataset(
        name="successful_dataset",
        fastq_folder=temporay_files["fastq"],
        metadata_path=temporay_files["meta"],
    )


def test_dataset_acctualy_get_fastq_files(temporay_files):
    file_count = 10
    for i in range(file_count):
        temporay_files["fastq"].joinpath(f"test{i}.fastq").touch()

    dataset = Dataset(
        name="test_dataset",
        fastq_folder=temporay_files["fastq"],
        metadata_path=temporay_files["meta"],
    )
    assert len(dataset.fastq_files) == file_count  # No fastq files in the temp file


def test_databank_instance_has_current_attributes():
    with NamedTemporaryFile(delete=True) as fastq_file:
        with NamedTemporaryFile(delete=True) as metadata_file:
            dataset = Dataset(
                name="test_dataset",
                fastq_folder=Path(fastq_file.name),
                metadata_path=Path(metadata_file.name),
            )
            databank = Databank(sets={dataset})
            assert databank.test_dataset == dataset
