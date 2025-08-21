from pathlib import Path
from typing import Tuple
from scripts.data.control.check_manifest import check_manifest
from scripts.data.control.create_Mfiles import create_Mfiles
from scripts.data.store.dataset import Datasets


def setup_files(output: Path, datasets: Datasets) -> Tuple[Path, Path]:
    create_Mfiles(
        id_prefix="id",
        out_meta=(metafile := output / "metadata.csv"),
        out_mani=(manifest := output / "manifest.csv"),
        data=datasets,
    )

    if not check_manifest(manifest):
        raise ValueError("Manifest file is invalid")

    return Path(metafile), Path(manifest)
