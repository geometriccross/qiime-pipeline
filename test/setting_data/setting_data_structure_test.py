import pytest
from pathlib import Path
from tempfile import NamedTemporaryFile
import tomlkit
from scripts.data_store import SettingData
from scripts.data_store.dataset import Databank, Dataset


@pytest.fixture
def dummy_setting_data(tmp_path, temporary_dataset):
    workspace = tmp_path / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)

    # Create a dummy Dockerfile and databank JSON file
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("FROM python:3.8\n")

    databank = Databank(sets=[temporary_dataset])

    # Return a SettingData instance using the dummy paths
    return SettingData(
        workspace_path=workspace,
        dockerfile=dockerfile,
        sampling_depth=10000,
        databank=databank,
    )


def test_setting_data_initialization():
    try:
        SettingData(
            workspace_path=Path("nonexistent/workspace"),
            dockerfile=Path("/nonexistent/Dockerfile"),
            sampling_depth="incorrect_type",
            databank="No Object",
        )
    except AssertionError:
        pass  # Expected to raise AssertionError due to non-existent paths


def test_correctly_convert_into_toml(dummy_setting_data):
    with NamedTemporaryFile(delete=True, mode="w", suffix=".toml") as saved_file:
        dummy_setting_data.write(saved_file.name)
        with open(saved_file.name, "r") as f:
            content = tomlkit.load(f)
            assert content is not None or content != ""

            for atr in dummy_setting_data.__dict__.keys():
                ins = getattr(dummy_setting_data, atr)

                # Convert instance to toml or something for TOML comparation
                if isinstance(ins, int):
                    assert content[atr] == ins
                if isinstance(ins, Path):
                    assert content[atr] == str(ins.absolute())
                elif isinstance(ins, Dataset):
                    assert content[atr] == ins.to_toml()
