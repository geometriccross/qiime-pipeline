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
            for i, line in enumerate(f.readlines()[1:], start=1):  # ヘッダーを除く
                csv = line.split("\t")
                assert csv[0] == f"id{i}"
                assert csv[1] == f"test{i}"
