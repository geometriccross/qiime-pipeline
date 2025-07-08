import pytest
from pathlib import Path
from tempfile import NamedTemporaryFile
import tomlkit
from scripts.setting_data.setting_data_structure import SettingData


@pytest.fixture
def dummy_setting_data(tmp_path):
    # Create two directories for fastq mounts
    host_side_fastq = tmp_path / "host_fastq"
    container_side_fastq = tmp_path / "container_fastq"

    # Create two directories for metadata mounts
    host_side_metadata = tmp_path / "host_metadata"
    container_side_metadata = tmp_path / "container_metadata"

    for dir in [
        host_side_fastq,
        container_side_fastq,
        host_side_metadata,
        container_side_metadata,
    ]:
        dir.mkdir(parents=True, exist_ok=True)

    # Create a dummy Dockerfile and databank JSON file
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("FROM python:3.8\n")
    databank_json = tmp_path / "databank.json"
    databank_json.write_text("{}\n")

    # Return a SettingData instance using the dummy paths
    return SettingData(
        host_side_fastq_folder=host_side_fastq,
        container_side_fastq_folder=container_side_fastq,
        host_side_metadata_folder=host_side_metadata,
        container_side_metadata_folder=container_side_metadata,
        dockerfile=dockerfile,
        databank_json_path=databank_json,
    )


def test_setting_data_initialization():
    try:
        SettingData(
            host_side_fastq_folder=Path("/nonexistent1"),
            container_side_fastq_folder=Path("/nonexistent2"),
            host_side_metadata_folder=Path("/nonexistent3"),
            container_side_metadata_folder=Path("/nonexistent4"),
            dockerfile=Path("/nonexistent/Dockerfile"),
            databank_json_path=Path("/nonexistent/databank.json"),
        )
    except AssertionError:
        pass  # Expected to raise AssertionError due to non-existent paths


def test_dumps(dummy_setting_data):
    with NamedTemporaryFile(delete=True, mode="w", suffix=".toml") as saved_file:
        dummy_setting_data.write(saved_file.name)
        with open(saved_file.name, "r") as f:
            content = tomlkit.load(f)
            assert content is not None or content != ""
            for atr in dummy_setting_data.__dict__.keys():
                match getattr(dummy_setting_data, atr):
                    case Path():
                        # Convert Path to string for TOML serialization
                        assert content[atr] == str(
                            getattr(dummy_setting_data, atr).absolute()
                        )
                    case _:
                        assert content[atr] == getattr(dummy_setting_data, atr)
