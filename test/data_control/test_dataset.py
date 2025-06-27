import json
import pytest
from pathlib import Path
from scripts.data_control.dataset import Dataset, Databank


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


def test_databank_instance_has_current_attributes(temporay_files):
    dataset = Dataset(
        name="test_dataset",
        fastq_folder=temporay_files["fastq"],
        metadata_path=temporay_files["meta"],
    )
    databank = Databank(sets={dataset})
    assert databank.test_dataset == dataset


def test_dataset_serialization(temporay_files):
    """Datasetのシリアライズとデシリアライズのテスト"""
    # テストデータの作成
    dataset = Dataset(
        name="test_dataset",
        fastq_folder=temporay_files["fastq"],
        metadata_path=temporay_files["meta"],
    )

    # シリアライズのテスト
    json_str = dataset.to_json()
    data = json.loads(json_str)
    assert data["name"] == "test_dataset"
    assert data["fastq_folder"] == str(temporay_files["fastq"])
    assert data["metadata_path"] == str(temporay_files["meta"])

    # デシリアライズのテスト
    restored = Dataset.from_json(json_str)
    assert restored.name == dataset.name
    assert restored.fastq_folder == dataset.fastq_folder
    assert restored.metadata_path == dataset.metadata_path


def test_databank_serialization(temporay_files):
    """Databankのシリアライズとデシリアライズのテスト"""
    dataset1 = Dataset(
        name="test_dataset1",
        fastq_folder=temporay_files["fastq"],
        metadata_path=temporay_files["meta"],
    )
    databank = Databank(sets={dataset1})

    # シリアライズとデシリアライズ
    json_str = databank.to_json()
    restored = Databank.from_json(json_str)

    assert len(restored.sets) == 1
    assert restored.test_dataset1.name == dataset1.name


def test_serialization_error_handling():
    """無効なJSONからのデシリアライズテスト"""
    invalid_json = '{"invalid": "json"}'

    with pytest.raises(KeyError):
        Dataset.from_json(invalid_json)

    with pytest.raises(KeyError):
        Databank.from_json(invalid_json)
