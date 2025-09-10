from pathlib import Path
from tempfile import TemporaryDirectory, NamedTemporaryFile
from scripts.data.store import Dataset, Datasets, Region


def test_dataset_raise_error_when_specify_incorrect_path(temporay_files):
    def check(fastq_folder, metadata_path, err_msg):
        try:
            Dataset(
                name="test_dataset",
                fastq_folder=fastq_folder,
                metadata_path=metadata_path,
                region=Region("SampleRegion", 0, 0, 0, 0),
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
        region=Region("SampleRegion", 0, 0, 0, 0),
    )


def test_dataset_acctualy_get_fastq_files(temporay_files):
    file_count = 10
    for i in range(file_count):
        temporay_files["fastq"].joinpath(f"test{i}.fastq").touch()

    dataset = Dataset(
        name="test_dataset",
        fastq_folder=temporay_files["fastq"],
        metadata_path=temporay_files["meta"],
        region=Region("SampleRegion", 0, 0, 0, 0),
    )
    assert len(dataset.fastq_files) == file_count  # No fastq files in the temp file
    for fastq, base in zip(
        sorted(dataset.fastq_files), sorted(temporay_files["fastq"].iterdir())
    ):
        assert fastq == base


def test_relative_fastq_path():
    fastq_dir = Path(TemporaryDirectory().name) / "foo/bar/baz/test"
    fastq_dir.mkdir(parents=True, exist_ok=True)

    fastq_file = fastq_dir / "test_R1.fastq.gz"
    fastq_file.touch()

    dataset = Dataset(
        name="test",
        fastq_folder=fastq_dir,
        metadata_path=Path(NamedTemporaryFile(delete=False).name),
        region=Region("SampleRegion", 0, 0, 0, 0),
    )

    relative_path = str(dataset.relative_fastq_path().pop())
    assert "foo/bar/baz" not in relative_path
    assert str(relative_path) == "test/test_R1.fastq.gz"


def test_dataset_conversion_to_toml(temporary_dataset):
    """DatasetのTOML形式への変換テスト"""
    toml_doc = temporary_dataset.to_toml()

    assert toml_doc["name"] == temporary_dataset.name
    assert toml_doc["fastq_folder"] == str(temporary_dataset.fastq_folder)
    assert toml_doc["metadata_path"] == str(temporary_dataset.metadata_path)
    assert toml_doc["region"] == temporary_dataset.region.to_toml()


def test_dataset_from_toml(temporary_dataset):
    toml_doc = temporary_dataset.to_toml()
    dataset = Dataset.from_toml(toml_doc)

    assert dataset.name == toml_doc["name"]
    assert dataset.fastq_folder == Path(toml_doc["fastq_folder"])
    assert dataset.metadata_path == Path(toml_doc["metadata_path"])
    assert dataset.region.to_toml() == toml_doc["region"]


def test_datasets_instance_has_current_attributes(temporary_dataset):
    datasets = Datasets(sets={temporary_dataset})
    assert datasets.test_dataset == temporary_dataset


def test_datasets_serialization(temporary_dataset):
    datasets = Datasets(sets={temporary_dataset})
    toml_doc = datasets.to_toml()

    assert toml_doc["sets"][0] == temporary_dataset.to_toml()


def test_datasets_from_toml(temporary_dataset):
    datasets = Datasets(sets={temporary_dataset})
    toml_doc = datasets.to_toml()
    new_datasets = Datasets.from_toml(toml_doc)

    assert len(new_datasets.sets) == 1
    assert new_datasets.sets.pop() == temporary_dataset
