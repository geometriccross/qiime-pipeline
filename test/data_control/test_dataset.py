from pathlib import Path
from tempfile import NamedTemporaryFile
from scripts.data_control.dataset import Dataset


def test_dataset_raise_error_when_specify_incorrect_path():
    def check(fastq_path, metadata_path, err_msg):
        try:
            Dataset(
                name="test_dataset",
                fastq_path=fastq_path,
                metadata_path=metadata_path,
            )
        except FileNotFoundError as e:
            assert str(e) == err_msg

    check(
        fastq_path=Path("non_existent.fastq"),
        metadata_path=Path("non_existent_metadata.tsv"),
        err_msg="Fastq path non_existent.fastq does not exist.",
    )

    with NamedTemporaryFile(delete=True) as fastq_file:
        check(
            fastq_path=Path(fastq_file.name),
            metadata_path=Path("non_existent_metadata.tsv"),
            err_msg="Metadata path non_existent_metadata.tsv does not exist.",
        )

        with NamedTemporaryFile(delete=True) as metadata_file:
            assert Dataset(
                name="successful_dataset",
                fastq_path=Path(fastq_file.name),
                metadata_path=Path(metadata_file.name),
            )
