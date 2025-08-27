from pathlib import Path
from scripts.pipeline.support.qiime_command import QiimeCommandBuilder


def test_basic_command():
    """基本的なコマンド構築のテスト"""
    cmd = QiimeCommandBuilder("qiime tools import").build()
    assert cmd[0] == "qiime tools import"
    assert len(cmd) == 1


def test_add_input():
    """inputパラメータ追加のテスト"""
    cmd = QiimeCommandBuilder("qiime dada2").add_input("sequences", "input.qza").build()
    assert "    --i-sequences input.qza" in cmd


def test_add_output():
    """outputパラメータ追加のテスト"""
    cmd = QiimeCommandBuilder("qiime dada2").add_output("table", "output.qza").build()
    assert "    --o-table output.qza" in cmd


def test_add_parameter():
    """パラメータ追加のテスト"""
    cmd = (
        QiimeCommandBuilder("qiime dada2")
        .add_parameter("trim-left-f", "17")
        .add_parameter("trim-left-r", "21")
        .build()
    )
    assert "    --p-trim-left-f 17" in cmd
    assert "    --p-trim-left-r 21" in cmd


def test_add_metadata():
    """metadataパラメータ追加のテスト"""
    cmd = (
        QiimeCommandBuilder("qiime diversity")
        .add_metadata("metadata-file", "metadata.tsv")
        .build()
    )
    assert "    --m-metadata-file metadata.tsv" in cmd


def test_add_option():
    """オプション追加のテスト"""
    # 値ありのオプション
    cmd1 = QiimeCommandBuilder("qiime tools").add_option("type", "SampleData").build()
    assert "    --type SampleData" in cmd1

    # 値なしのオプション
    cmd2 = QiimeCommandBuilder("qiime dada2").add_option("quiet").build()
    assert "    --quiet" in cmd2


def test_method_chaining():
    """メソッドチェーンのテスト"""
    cmd = (
        QiimeCommandBuilder("qiime dada2")
        .add_input("sequences", "input.qza")
        .add_output("table", "output.qza")
        .add_parameter("trim-left-f", "17")
        .add_metadata("metadata-file", "metadata.tsv")
        .add_option("quiet")
        .build()
    )
    assert len(cmd) == 6
    assert cmd[0] == "qiime dada2"
    assert "    --i-sequences input.qza" in cmd
    assert "    --o-table output.qza" in cmd
    assert "    --p-trim-left-f 17" in cmd
    assert "    --m-metadata-file metadata.tsv" in cmd
    assert "    --quiet" in cmd


def test_path_handling():
    """Pathオブジェクトの処理テスト"""
    input_path = Path("data/input.qza")
    output_path = Path("results/output.qza")
    cmd = (
        QiimeCommandBuilder("qiime tools")
        .add_input("sequences", input_path)
        .add_output("table", output_path)
        .build()
    )
    assert "    --i-sequences data/input.qza" in cmd
    assert "    --o-table results/output.qza" in cmd


def test_empty_values():
    """空文字列の処理テスト"""
    cmd = (
        QiimeCommandBuilder("qiime tools")
        .add_parameter("threads", "")
        .add_option("type", "")
        .build()
    )
    assert "    --p-threads " in cmd
    assert "    --type" in cmd


def test_indentation_consistency():
    """インデントの一貫性テスト"""
    cmd = (
        QiimeCommandBuilder("qiime tools")
        .add_input("seq", "in.qza")
        .add_output("tab", "out.qza")
        .add_parameter("trim", "10")
        .add_metadata("meta", "meta.tsv")
        .add_option("quiet")
        .build()
    )

    # ベースコマンド以外の全ての行が4スペースでインデントされていることを確認
    for line in cmd[1:]:
        assert line.startswith("    --")
        # インデント以降の部分が正しいプレフィックスで始まることを確認
        rest = line.lstrip()
        assert rest.startswith("--")
