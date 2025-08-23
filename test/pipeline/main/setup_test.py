from pathlib import Path
from tempfile import TemporaryDirectory
from scripts.pipeline.main.setup import setup_files
from scripts.data.store.dataset import Datasets


def test_setup_files_currently_created(dummy_datasets: Datasets):
    with TemporaryDirectory() as out:
        meta, manifest = setup_files(Path(out), dummy_datasets)

        assert Path(meta).exists()
        assert Path(manifest).exists()

        with open(meta) as f:
            lines = f.readlines()
            for i, line in enumerate(lines, start=1):
                assert f"test{i}" in line
