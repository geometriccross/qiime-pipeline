from scripts.pipeline.support import Q2CmdAssembly


def test_Q2CmdAssembly_convert_to_str():
    assembly = Q2CmdAssembly("qiime tools import")
    assert str(assembly) == "qiime tools import"


def test_get_paths():
    cmd = Q2CmdAssembly("qiime tools import")
    cmd.add_input("data", "input1.qza")
    cmd.add_input("mapping", "input2.qza")

    paths = cmd._get_paths_from_parts("--i-")
    assert len(paths) == 2
    assert "input1.qza" in paths
    assert "input2.qza" in paths


def test_command_ordering():
    """コマンド順序付けのテスト"""
    # ケース1: 直接的な依存関係あり
    cmd1 = Q2CmdAssembly("cmd1").add_output("out", "file1.qza")
    cmd2 = Q2CmdAssembly("cmd2").add_input("in", "file1.qza")
    assert cmd1 < cmd2  # cmd1が先に実行される
    assert cmd2 > cmd1  # cmd2は後に実行される
    assert not cmd2 < cmd1  # 逆の関係は成り立たない

    # ケース2: 依存関係なし
    cmd3 = Q2CmdAssembly("cmd3").add_input("in", "other.qza")
    assert cmd1 == cmd3  # 順序は同等
    assert not cmd1 < cmd3
    assert not cmd3 < cmd1

    # ケース3: 複数の依存関係
    cmd4 = (
        Q2CmdAssembly("cmd4")
        .add_input("in1", "cmd4_input.qza")
        .add_output("in2", "cmd4_output.qza")
    )
    cmd5 = (
        Q2CmdAssembly("cmd5")
        .add_input("in", "cmd4_output.qza")
        .add_output("out", "final_output.qza")
    )
    assert cmd4 < cmd5


def test_command_chaining():
    """コマンドチェーンのテスト"""
    # インポート → 処理 → エクスポートの順序チェック
    import_cmd = (
        Q2CmdAssembly("qiime tools import")
        .add_input("data", "raw.fastq")
        .add_output("output-seq", "imported_seq.qza")
        .add_output("output-table", "imported_table.qza")
    )

    process_cmd = (
        Q2CmdAssembly("qiime process")
        .add_input("data", "imported-seq.qza")
        .add_output("output", "processed.qza")
    )

    export_cmd = (
        Q2CmdAssembly("qiime tools export")
        .add_input("data", "imported_table.qza")
        .add_input("data", "processed.qza")
        .add_output("output", "final.qza")
    )

    # 順序関係の検証
    assert import_cmd < process_cmd
    assert process_cmd < export_cmd
    assert import_cmd < export_cmd  # 推移的な関係も成り立つ

    # リストのソートで正しい順序になることを確認
    commands = [export_cmd, import_cmd, process_cmd]
    sorted_commands = sorted(commands)
    assert str(sorted_commands[0]) == str(import_cmd)
    assert str(sorted_commands[1]) == str(process_cmd)
    assert str(sorted_commands[2]) == str(export_cmd)
