import pytest
from tempfile import TemporaryDirectory
from pathlib import Path
from argparse import Namespace
from scripts.pipeline.support.setup import setup_datasets


@pytest.fixture
def namespace(data_path_pairs) -> Namespace:
    with TemporaryDirectory() as tmp_dir:
        return Namespace(
            dockerfile=Path("dockerfiles/Dockerfile"),
            sampling_depth=10000,
            data=data_path_pairs,
            # 適当なところから、TemporaryDirectoryのpathを取得
            workspace_path=data_path_pairs[0][1],
            output=Path(tmp_dir),
        )


def test_setup_datasets(namespace):
    datasets = setup_datasets(namespace)
    assert datasets is not None
    assert len(datasets.sets) == 4  # data_path_pairで生成したものが4つのため

    for datasets in datasets.sets:
        assert datasets.name in ["test1", "test2", "test3", "test4"]
        assert datasets.fastq_folder.exists()
        assert datasets.metadata_path.exists()
        assert datasets.region is not None
