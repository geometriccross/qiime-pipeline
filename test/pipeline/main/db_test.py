import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch, MagicMock, mock_open
from python_on_whales import Container

from scripts.pipeline.main.db import DatabaseBuilder


class TestDatabaseBuilder(TestCase):
    def setUp(self):
        self.container = MagicMock(spec=Container)
        self.mock_executor = MagicMock()
        self.temp_dir = Path(tempfile.mkdtemp())

    @patch("scripts.pipeline.main.db.os.path.exists")
    def test_init_fails_outside_container(self, mock_exists):
        mock_exists.return_value = False

        with self.assertRaises(RuntimeError) as context:
            DatabaseBuilder(self.container)

        self.assertIn("コンテナ内で実行する必要があります", str(context.exception))

    @patch("scripts.pipeline.main.db.os.path.exists")
    @patch("scripts.pipeline.main.db.requests.get")
    @patch("scripts.pipeline.main.db.Executor")
    def test_build_downloads_and_processes_files(
        self, mock_executor_class, mock_requests_get, mock_exists
    ):
        # セットアップ
        mock_exists.return_value = True
        mock_executor = mock_executor_class.return_value
        mock_executor.run.return_value = ("", "")  # 成功を示す空のエラー出力

        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b"data"]
        mock_requests_get.return_value = mock_response

        # テスト実行
        with patch("builtins.open", mock_open()):
            builder = DatabaseBuilder(self.container)
            result = builder.build()

        # アサーション
        self.assertTrue(result.endswith("classifier-silva138.qza"))
        self.assertEqual(mock_requests_get.call_count, 2)  # 2つのファイルをダウンロード
        self.assertEqual(mock_executor.run.call_count, 2)  # 2つのQIIMEコマンドを実行

    @patch("scripts.pipeline.main.db.os.path.exists")
    @patch("scripts.pipeline.main.db.requests.get")
    def test_download_file_handles_errors(self, mock_requests_get, mock_exists):
        mock_exists.return_value = True
        mock_requests_get.side_effect = Exception("Download failed")

        with self.assertRaises(Exception):
            builder = DatabaseBuilder(self.container)
            builder._download_files()

    @patch("scripts.pipeline.main.db.os.path.exists")
    @patch("scripts.pipeline.main.db.Executor")
    def test_extract_reads_handles_errors(self, mock_executor_class, mock_exists):
        mock_exists.return_value = True
        mock_executor = mock_executor_class.return_value
        mock_executor.run.return_value = ("", "Error occurred")

        with self.assertRaises(RuntimeError) as context:
            builder = DatabaseBuilder(self.container)
            builder._extract_reads()

        self.assertIn("リファレンスシーケンスの抽出に失敗", str(context.exception))

    @patch("scripts.pipeline.main.db.os.path.exists")
    @patch("scripts.pipeline.main.db.Executor")
    def test_train_classifier_handles_errors(self, mock_executor_class, mock_exists):
        mock_exists.return_value = True
        mock_executor = mock_executor_class.return_value
        mock_executor.run.return_value = ("", "Error occurred")

        with self.assertRaises(RuntimeError) as context:
            builder = DatabaseBuilder(self.container)
            builder._train_classifier()

        self.assertIn("DBの学習に失敗", str(context.exception))
