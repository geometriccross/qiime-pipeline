import os
import tempfile
import requests
from pathlib import Path
from python_on_whales import Container
from scripts.pipeline.support.executor import Executor
from scripts.pipeline.support.qiime_command import Q2CmdAssembly


class DatabaseBuilder:
    """SILVAデータベースのダウンロードとQIIME2用のデータベース構築を行うクラス"""

    SILVA_SEQS_URL = "https://data.qiime2.org/2024.10/common/silva-138-99-seqs.qza"
    SILVA_TAX_URL = "https://data.qiime2.org/2024.10/common/silva-138-99-tax.qza"

    def __init__(self, container: Container):
        """
        Args:
            container: 実行用のDockerコンテナ
        """
        if not self._is_in_container():
            raise RuntimeError(
                "このスクリプトはDockerコンテナ内で実行する必要があります"
            )

        self.executor = Executor(container)
        self.temp_dir = Path(tempfile.mkdtemp())

    def build(self) -> str:
        """データベースの構築を実行する

        Returns:
            str: 構築されたclassifierファイルの絶対パス
        """
        self._download_files()
        self._extract_reads()
        self._train_classifier()

        classifier_path = self.temp_dir / "classifier-silva138.qza"
        return str(classifier_path.absolute())

    def _is_in_container(self) -> bool:
        """Dockerコンテナ内で実行されているかチェックする"""
        return os.path.exists("/.dockerenv")

    def _download_files(self):
        """SILVAデータベースのファイルをダウンロードする"""
        self._download_file(self.SILVA_SEQS_URL, "silva-138-99-seqs.qza")
        self._download_file(self.SILVA_TAX_URL, "silva-138-99-tax.qza")

    def _download_file(self, url: str, filename: str):
        """指定されたURLからファイルをダウンロードする

        Args:
            url: ダウンロードするファイルのURL
            filename: 保存するファイル名
        """
        response = requests.get(url, stream=True)
        response.raise_for_status()

        filepath = self.temp_dir / filename
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

    def _extract_reads(self):
        """リファレンスシーケンスを抽出する"""
        command = (
            Q2CmdAssembly("qiime feature-classifier extract-reads")
            .add_parameter("min-length", "350")
            .add_parameter("max-length", "500")
            .add_parameter("f-primer", "CCTACGGGNGGCWGCAG")
            .add_parameter("r-primer", "GACTACHVGGGTATCTAATCC")
            .add_input("sequences", str(self.temp_dir / "silva-138-99-seqs.qza"))
            .add_output("reads", str(self.temp_dir / "ref-seqs-silva-138.qza"))
            .build()
        )

        output, error = self.executor.run(command)
        if error:
            raise RuntimeError(f"リファレンスシーケンスの抽出に失敗しました: {error}")

    def _train_classifier(self):
        """DBを学習する"""
        command = (
            Q2CmdAssembly("qiime feature-classifier fit-classifier-naive-bayes")
            .add_input("reference-reads", str(self.temp_dir / "ref-seqs-silva-138.qza"))
            .add_input(
                "reference-taxonomy", str(self.temp_dir / "silva-138-99-tax.qza")
            )
            .add_output("classifier", str(self.temp_dir / "classifier-silva138.qza"))
            .build()
        )

        output, error = self.executor.run(command)
        if error:
            raise RuntimeError(f"DBの学習に失敗しました: {error}")
