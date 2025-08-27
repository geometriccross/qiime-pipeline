from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from scripts.pipeline.main.sampling_and_rarefaction import (
    run_rarefaction,
    run_sampling_depth,
    execute,
)
from scripts.pipeline.support.executor import Executor


# テスト用の定数
TEST_QZV_PATH = Path("alpha_rarefaction.qzv")
TEST_BATCH_ID = "test_batch"


@pytest.fixture
def mock_setting(dummy_datasets, tmp_path):
    """テスト用のSettingData"""
    metadata_path = tmp_path / "metadata.tsv"
    metadata_path.write_text("#SampleID,feature1\ntest1,value1\n")

    manifest_path = tmp_path / "manifest.csv"
    manifest_path.write_text(
        "#SampleID,forward-absolute-filepath,reverse-absolute-filepath\n"
        "test1,R1.fastq,R2.fastq\n"
    )

    return MagicMock(
        manifest_path=manifest_path,
        metadata_path=metadata_path,
        datasets=dummy_datasets,
        batch_id=TEST_BATCH_ID,
    )


@pytest.fixture
def mock_executor():
    """テスト用のExecutor"""
    executor = MagicMock(spec=Executor)
    executor.run.return_value = (str(TEST_QZV_PATH), "")
    return executor


def test_run_rarefaction(mock_setting, mock_executor):
    """run_rarefaction関数のテスト

    以下を確認:
    1. 必要なQIIMEコマンドが正しい順序で実行される
    2. コマンドに必要なパラメータが含まれている
    3. 正しいQZVファイルパスが返される

    期待される実行順序:
    1. 作業ディレクトリの作成
    2. QIIME tools import
    3. QIIME dada2 denoise-paired
    4. QIIME phylogeny align-to-tree-mafft-fasttree
    5. QIIME diversity alpha-rarefaction
    """
    result = run_rarefaction(mock_setting, mock_executor)

    # コマンドの実行回数を確認
    assert mock_executor.run.call_count == 5

    # 各コマンドの呼び出しを順序通りに確認
    calls = mock_executor.run.call_args_list
    expected_commands = [
        "mkdir",  # 作業ディレクトリの作成
        "qiime tools import",  # マニフェストファイルのインポート
        "qiime dada2 denoise-paired",  # ペアエンドシーケンスの解析
        "qiime phylogeny align-to-tree-mafft-fasttree",  # 系統樹の構築
        "qiime diversity alpha-rarefaction",  # レアレファクション分析
    ]

    for i, command in enumerate(expected_commands):
        assert command in str(
            calls[i]
        ), f"期待される{i+1}番目のコマンド '{command}' が実行されていません"

    # 各コマンドの重要なパラメータを確認
    rarefaction_cmd = str(calls[4])
    assert "--i-table" in rarefaction_cmd, "入力テーブルが指定されていません"
    assert "--i-phylogeny" in rarefaction_cmd, "系統樹が指定されていません"
    assert "--p-max-depth" in rarefaction_cmd, "最大深度が指定されていません"
    assert "--o-visualization" in rarefaction_cmd, "出力ファイルが指定されていません"

    # 返値を確認
    assert isinstance(result, Path)
    assert str(result) == str(TEST_QZV_PATH)


def test_run_sampling_depth(mock_setting, mock_executor):
    """run_sampling_depth関数のテスト

    以下を確認:
    1. Docker CPコマンドが正しく実行される
    2. バッチIDとQZVファイルパスが正しく使用される
    """
    qzv_path = TEST_QZV_PATH
    run_sampling_depth(mock_setting, mock_executor, qzv_path)

    # docker cpコマンドが実行されたことを確認
    docker_cp_call = mock_executor.run.call_args_list[0]
    assert "docker" in str(docker_cp_call)
    assert "cp" in str(docker_cp_call)
    assert mock_setting.batch_id in str(docker_cp_call)
    assert str(qzv_path) in str(docker_cp_call)


def test_execute(mock_setting, mock_executor):
    """execute関数のテスト

    以下を確認:
    1. 正常系：コマンドが実行され、エラーが発生しない
    2. 異常系：例外が適切に伝播される
    """
    # 正常系
    execute(mock_setting, mock_executor)
    assert mock_executor.run.called

    # 異常系
    mock_executor.run.side_effect = Exception("Test error")
    with pytest.raises(Exception) as exc_info:
        execute(mock_setting, mock_executor)
    assert "Test error" in str(exc_info.value)


def test_execute_creates_output_directory(mock_setting, mock_executor):
    """出力ディレクトリの作成テスト

    以下を確認:
    1. 実行前にディレクトリが存在しない場合、作成される
    2. mkdirコマンドが正しいパスで実行される
    """
    out_dir = Path(f"out/{mock_setting.batch_id}")

    # 実行前にディレクトリが存在しないことを確認
    if out_dir.exists():
        out_dir.rmdir()

    execute(mock_setting, mock_executor)

    # ディレクトリが作成されたことを確認
    mock_executor.run.assert_any_call(["mkdir", "-p", str(Path("/tmp/out"))])


@patch("pathlib.Path.glob")
def test_qzv_file_processing(mock_glob, mock_setting, mock_executor):
    """QZVファイルの処理テスト

    以下を確認:
    1. glob関数が正しく呼び出される
    2. 見つかった各QZVファイルに対してview.shが実行される
    3. Docker CP処理が正しく実行される
    """
    # テストデータの設定
    test_qzv_files = [
        Path(f"out/{TEST_BATCH_ID}/result1.qzv"),
        Path(f"out/{TEST_BATCH_ID}/result2.qzv"),
    ]
    mock_glob.return_value = test_qzv_files

    qzv_path = TEST_QZV_PATH
    run_sampling_depth(mock_setting, mock_executor, qzv_path)

    # view.shが各QZVファイルに対して実行されたことを確認
    view_sh_calls = [
        call_args
        for call_args in mock_executor.run.call_args_list
        if "./scripts/view.sh" in str(call_args)
    ]
    assert len(view_sh_calls) == 2  # 2つのQZVファイルそれぞれに対して実行
