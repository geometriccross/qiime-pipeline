#!/usr/bin/env python

import csv
import pytest
from pathlib import Path
from typing import List
from scripts.create_Mfiles import (
    FastqProcessor,
    MetadataProcessor,
    FastqFileNotFoundError,
    DuplicateFastqError,
)
from scripts.config import DataSource


@pytest.fixture
def sample_fastq_files(tmp_path) -> List[str]:
    """FASTQファイルのモックを作成"""
    fastq_dir = tmp_path / "fastq"
    fastq_dir.mkdir()

    # 正常なペア
    (fastq_dir / "SAMPLE1_R1_001.fastq.gz").touch()
    (fastq_dir / "SAMPLE1_R2_001.fastq.gz").touch()

    # 重複ファイル
    (fastq_dir / "DUPLICATE_R1_001.fastq.gz").touch()
    (fastq_dir / "DUPLICATE_R2_001.fastq.gz").touch()
    (fastq_dir / "DUPLICATE_OTHER.fastq.gz").touch()

    files = list(map(str, fastq_dir.glob("*.fastq.gz")))
    return files


@pytest.fixture
def sample_metadata(tmp_path) -> tuple[str, DataSource]:
    """メタデータファイルのモックを作成"""
    meta_dir = tmp_path / "meta"
    meta_dir.mkdir()

    meta_file = meta_dir / "test.csv"
    meta_content = (
        "#SampleID,col1,col2\n" "SAMPLE1,value1,value2\n" "SAMPLE2,value3,value4\n"
    )
    meta_file.write_text(meta_content)

    data_source: DataSource = {"meta": str(meta_file), "fastq": str(tmp_path / "fastq")}

    return str(meta_file), data_source


class TestFastqProcessor:
    """FastqProcessorのテストクラス"""

    def test_search_fastq_success(self, sample_fastq_files):
        """正常系: FASTQファイルペアを正しく検索できる"""
        processor = FastqProcessor()
        fwd, rvs = processor.search_fastq("SAMPLE1", sample_fastq_files)

        assert Path(fwd).name == "SAMPLE1_R1_001.fastq.gz"
        assert Path(rvs).name == "SAMPLE1_R2_001.fastq.gz"

    def test_search_fastq_not_found(self, sample_fastq_files):
        """異常系: 存在しないサンプルIDの場合はエラー"""
        processor = FastqProcessor()
        with pytest.raises(FastqFileNotFoundError):
            processor.search_fastq("NONEXISTENT", sample_fastq_files)

    def test_search_fastq_duplicate(self, sample_fastq_files):
        """異常系: 同名のファイルが3つ以上ある場合はエラー"""
        processor = FastqProcessor()
        with pytest.raises(DuplicateFastqError):
            processor.search_fastq("DUPLICATE", sample_fastq_files)


class TestMetadataProcessor:
    """MetadataProcessorのテストクラス"""

    def test_initialize_master_list(self, sample_metadata):
        """マスターリストの初期化が正しく行われる"""
        meta_file, _ = sample_metadata
        id_prefix = "test"
        processor = MetadataProcessor(id_prefix)
        processor.initialize_master_list(meta_file)

        expected_header = [
            id_prefix,
            "RawID",
            "col1",
            "col2",
        ]
        assert processor.master_list[0] == expected_header

    def test_initialize_manifest_list(self):
        """マニフェストリストの初期化が正しく行われる"""
        processor = MetadataProcessor("test")
        processor.initialize_manifest_list()

        expected_header = [
            "sample-id",
            "forward-absolute-filepath",
            "reverse-absolute-filepath",
        ]
        assert processor.manifest_list[0] == expected_header

    def test_process_metadata(self, sample_metadata, sample_fastq_files):
        """メタデータの処理が正しく行われる"""
        _, data_source = sample_metadata
        processor = MetadataProcessor("test")
        processor.initialize_master_list(data_source["meta"])
        processor.initialize_manifest_list()

        # サンプルのメタデータを処理
        processor.process_metadata([data_source])

        # マスターリストの検証
        assert len(processor.master_list) == 3  # ヘッダー + 2行
        assert processor.master_list[1][0] == "test1"  # 最初のサンプルID

        # マニフェストリストの検証
        assert (
            len(processor.manifest_list) == 2
        )  # ヘッダー + 1行（SAMPLE2は見つからないため）
        assert processor.manifest_list[1][0] == "test1"  # 最初のサンプルID


def test_end_to_end(tmp_path):
    """エンドツーエンドテスト"""
    # 出力ディレクトリの準備
    out_meta = tmp_path / "out_meta.tsv"
    out_mani = tmp_path / "out_manifest.tsv"

    # テストデータの準備
    fastq_dir = tmp_path / "fastq_test"
    fastq_dir.mkdir()
    (fastq_dir / "SAMPLE1_R1_001.fastq.gz").touch()
    (fastq_dir / "SAMPLE1_R2_001.fastq.gz").touch()

    meta_dir = tmp_path / "meta_test"
    meta_dir.mkdir()
    meta_file = meta_dir / "test.csv"
    meta_content = "#SampleID,col1,col2\nSAMPLE1,value1,value2\n"
    meta_file.write_text(meta_content)

    # データソースの設定
    data_source: DataSource = {"meta": str(meta_file), "fastq": str(fastq_dir)}

    # メタデータ処理
    processor = MetadataProcessor("test")
    processor.initialize_master_list(data_source["meta"])
    processor.initialize_manifest_list()
    processor.process_metadata([data_source])

    # 結果の保存
    with open(out_meta, "w") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerows(processor.master_list)

    with open(out_mani, "w") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerows(processor.manifest_list)

    # ファイルが生成されていることを確認
    assert out_meta.exists()
    assert out_mani.exists()

    # ファイルの内容を確認
    with open(out_meta) as f:
        meta_lines = f.readlines()
        assert len(meta_lines) == 2  # ヘッダー + 1行

    with open(out_mani) as f:
        mani_lines = f.readlines()
        assert len(mani_lines) == 2  # ヘッダー + 1行
