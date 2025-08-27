from scripts.pipeline.support.setup import setup_datasets


def test_setup_datasets(namespace):
    datasets = setup_datasets(namespace)
    assert datasets is not None
    assert len(datasets.sets) == 4  # data_path_pairで生成したものが4つのため

    for datasets in datasets.sets:
        assert datasets.name in ["test1", "test2", "test3", "test4"]
        assert datasets.fastq_folder.exists()
        assert datasets.metadata_path.exists()
        assert datasets.region is not None
