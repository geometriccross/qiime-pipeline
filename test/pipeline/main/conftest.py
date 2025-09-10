from pathlib import Path
import pytest
from scripts.pipeline.support import Executor

TEST_QZV_PATH = Path("alpha_rarefaction.qzv")
TEST_BATCH_ID = "test_batch"


@pytest.fixture
def mock_setting(dummy_datasets, tmp_path, mocker):
    """pytest-mockを使ったSettingDataのモック"""
    metadata_path = tmp_path / "metadata.tsv"
    metadata_path.write_text("#SampleID,feature1\ntest1,value1\n")

    manifest_path = tmp_path / "manifest.csv"
    manifest_path.write_text(
        "#SampleID,forward-absolute-filepath,reverse-absolute-filepath\n"
        "test1,R1.fastq,R2.fastq\n"
    )

    mock = mocker.MagicMock()
    mock.manifest_path = manifest_path
    mock.metadata_path = metadata_path
    mock.datasets = dummy_datasets
    mock.batch_id = TEST_BATCH_ID
    return mock


@pytest.fixture
def mock_executor(mocker):
    """pytest-mockを使ったExecutorのモック"""
    executor = mocker.MagicMock(spec=Executor)
    executor.run.return_value = (str(TEST_QZV_PATH), "")
    return executor


@pytest.fixture
def qzv_test_files(request, mocker):
    """QZVファイルとディレクトリを作成するpytest-mock用フィクスチャ"""
    out_dir = Path(f"out/{TEST_BATCH_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)

    import zipfile

    file_count = getattr(request, "param", 2)
    test_files = [out_dir / f"result{i+1}.qzv" for i in range(file_count)]
    for qzv_file in test_files:
        with zipfile.ZipFile(qzv_file, "w") as zf:
            zf.writestr("data/index.html", "<html></html>")

    yield test_files

    for qzv_file in test_files:
        if qzv_file.exists():
            qzv_file.unlink()
    if out_dir.exists():
        out_dir.rmdir()
