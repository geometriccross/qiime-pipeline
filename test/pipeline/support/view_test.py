import os
import pytest
from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import ZipFile
from src.pipeline.support.view import QzvViewer, ViewError


@pytest.fixture
def mock_env(monkeypatch):
    """環境変数をモック化"""
    monkeypatch.setenv("WSL_DISTRO_NAME", "Ubuntu")
    monkeypatch.setenv("BROWSER", "firefox")


@pytest.fixture
def mock_qzv_file():
    """テスト用のQZVファイルを作成"""
    with NamedTemporaryFile(suffix=".qzv", delete=False) as tmp_file:
        with ZipFile(tmp_file.name, "w") as zip_file:
            # data/index.htmlを作成
            zip_file.writestr("data/index.html", "<html><body>Test</body></html>")
        yield Path(tmp_file.name)
    # テスト後にファイルを削除
    os.unlink(tmp_file.name)


def test_validate_environment_success(mock_env):
    """環境変数が正しく設定されている場合のテスト"""
    QzvViewer()  # インスタンスを生成するだけで検証は完了する


def test_validate_environment_no_wsl(monkeypatch):
    """WSL環境変数が設定されていない場合のテスト"""
    monkeypatch.delenv("WSL_DISTRO_NAME", raising=False)
    with pytest.raises(ViewError, match="WSL環境で実行する必要があります"):
        QzvViewer()


def test_validate_environment_no_browser(monkeypatch):
    """BROWSER環境変数が設定されていない場合のテスト"""
    monkeypatch.setenv("WSL_DISTRO_NAME", "Ubuntu")
    monkeypatch.delenv("BROWSER", raising=False)
    with pytest.raises(ViewError, match="BROWSER環境変数が設定されていません"):
        QzvViewer()


def test_extract_index_html_success(mock_env, mock_qzv_file):
    """QZVファイルからindex.htmlが正しく展開できる場合のテスト"""
    viewer = QzvViewer()
    index_path = viewer._extract_index_html(mock_qzv_file)
    assert index_path.exists()
    assert index_path.name == "index.html"
    assert index_path.parent.name == "data"


def test_extract_index_html_invalid_file(mock_env):
    """存在しないQZVファイルを指定した場合のテスト"""
    viewer = QzvViewer()
    invalid_path = Path("nonexistent.qzv")
    with pytest.raises(ViewError, match="QZVファイルの展開に失敗しました"):
        viewer._extract_index_html(invalid_path)


def test_extract_index_html_missing_index(mock_env, tmp_path):
    """index.htmlが含まれていないQZVファイルの場合のテスト"""
    viewer = QzvViewer()
    qzv_path = tmp_path / "test.qzv"
    with ZipFile(qzv_path, "w") as zip_file:
        zip_file.writestr("data/other.html", "test")

    with pytest.raises(ViewError, match="index.htmlが見つかりません"):
        viewer._extract_index_html(qzv_path)


def test_view_file_not_found(mock_env):
    """存在しないファイルを表示しようとした場合のテスト"""
    viewer = QzvViewer()
    with pytest.raises(ViewError, match="ファイル .* が見つかりません"):
        viewer.view(Path("nonexistent.qzv"))


def test_cleanup(mock_env, mock_qzv_file):
    """一時ディレクトリが正しく削除されるかのテスト"""
    viewer = QzvViewer()
    viewer._extract_index_html(mock_qzv_file)
    temp_dir = viewer.temp_dir
    assert temp_dir.exists()
    viewer._cleanup()
    assert not temp_dir.exists()


def test_is_in_container(monkeypatch, tmp_path):
    """Dockerコンテナ環境の判定テスト"""
    from src.pipeline.support.view import _is_in_container

    # コンテナ外
    assert not _is_in_container()

    # コンテナ内
    dockerenv = tmp_path / ".dockerenv"
    dockerenv.touch()
    monkeypatch.setattr("os.path.exists", lambda x: x == "/.dockerenv")
    assert _is_in_container()
