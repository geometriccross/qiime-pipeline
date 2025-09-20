from scripts.pipeline.support import (
    Q2CmdAssembly,
    CircularDependencyError,
    IsolatedCommandError,
)


def test_Q2Cmd_convert_to_str():
    cmd = Q2CmdAssembly().new_cmd("qiime tools import")
    assert str(cmd) == "qiime tools import"


def test_get_paths():
    cmd = Q2CmdAssembly().new_cmd("qiime tools import")
    cmd.add_input("data", "input1.qza")
    cmd.add_input("mapping", "input2.qza")

    paths = cmd._get_paths_from_parts("--i-")
    assert len(paths) == 2
    assert "input1.qza" in paths
    assert "input2.qza" in paths


def test_command_ordering():
    """コマンド順序付けのテスト"""
    # ケース1: 直接的な依存関係あり
    cmd1 = Q2CmdAssembly().new_cmd("cmd1").add_output("out", "file1.qza")
    cmd2 = Q2CmdAssembly().new_cmd("cmd2").add_input("in", "file1.qza")
    assert cmd1 < cmd2  # cmd1が先に実行される
    assert cmd2 > cmd1  # cmd2は後に実行される
    assert not cmd2 < cmd1  # 逆の関係は成り立たない

    # ケース2: 依存関係なし
    cmd3 = Q2CmdAssembly().new_cmd("cmd3").add_input("in", "other.qza")
    assert not cmd1 < cmd3
    assert not cmd3 < cmd1

    # ケース3: 複数の依存関係
    cmd4 = (
        Q2CmdAssembly()
        .new_cmd("cmd4")
        .add_input("in1", "cmd4_input.qza")
        .add_output("in2", "cmd4_output.qza")
    )
    cmd5 = (
        Q2CmdAssembly()
        .new_cmd("cmd5")
        .add_input("in", "cmd4_output.qza")
        .add_output("out", "final_output.qza")
    )
    assert cmd4 < cmd5


def test_command_chaining():
    """コマンドチェーンのテスト"""
    assembly = Q2CmdAssembly()

    # インポート → 処理 → エクスポートの順序チェック
    import_cmd = assembly.new_cmd("qiime tools import")
    import_cmd.add_input("data", "raw.fastq")
    import_cmd.add_output("output-seq", "imported-seq.qza")
    import_cmd.add_output("output-table", "imported-table.qza")

    process1_cmd = assembly.new_cmd("qiime process1")
    process1_cmd.add_input("data", "imported-seq.qza")
    process1_cmd.add_output("output", "processed-seq.qza")

    process2_cmd = assembly.new_cmd("qiime process2")
    process2_cmd.add_input("data", "imported-table.qza")
    process2_cmd.add_output("output", "processed-table.qza")

    export_cmd = assembly.new_cmd("qiime tools export")
    export_cmd.add_input("data", "processed-seq.qza")
    export_cmd.add_input("data", "processed-table.qza")
    export_cmd.add_output("output", "final.qza")

    # 逆順でコマンドを追加（ソートにより正しい順序になることを確認）
    assembly.commands = [export_cmd, process2_cmd, process1_cmd, import_cmd]

    # 依存関係に基づいてソート
    assembly.sort_commands()

    # 依存関係の順序を確認
    assert str(assembly.commands[0]) == str(import_cmd)  # インポートが最初
    assert str(assembly.commands[3]) == str(export_cmd)  # エクスポートが最後

    # process1とprocess2は並列実行可能なので、どちらが先でもOK
    process_cmds = [str(cmd) for cmd in assembly.commands[1:3]]
    assert str(process1_cmd) in process_cmds
    assert str(process2_cmd) in process_cmds


def test_circular_dependency():
    """循環依存関係の検出とエラーメッセージのテスト"""
    cyclic_assembly = Q2CmdAssembly()
    cmd1 = cyclic_assembly.new_cmd("cmd1")
    cmd1.add_input("in", "input1.qza")
    cmd1.add_output("out", "file1.qza")

    cmd2 = cyclic_assembly.new_cmd("cmd2")
    cmd2.add_input("in", "file1.qza")
    cmd2.add_output("out", "file2.qza")

    cmd3 = cyclic_assembly.new_cmd("cmd3")
    cmd3.add_input("in", "file2.qza")
    cmd3.add_output("out", "input1.qza")  # cmd1を参照する

    try:
        cyclic_assembly.sort_commands()
        assert False, "循環依存関係が検出されるべき"
    except CircularDependencyError as e:
        error_msg = str(e)
        # エラーメッセージに全てのコマンドが含まれていることを確認
        assert "cmd1" in error_msg
        assert "cmd2" in error_msg
        assert "cmd3" in error_msg

        # 依存関係の順序が正しく表示されていることを確認
        # cmd1 <- cmd3: cmd3の出力がcmd1の入力として使用される
        assert "cmd1 <- cmd3" in error_msg
        assert "cmd3 <- cmd2" in error_msg
        assert "cmd2 <- cmd1" in error_msg


def test_isolated_command():
    """孤立したコマンドの検出テスト"""
    assembly = Q2CmdAssembly()

    # 孤立したコマンドを作成
    isolated_cmd = assembly.new_cmd("qiime isolated-command")
    isolated_cmd.add_input("in", "isolated.qza")
    isolated_cmd.add_output("out", "isolated_out.qza")

    # 依存関係のある2つのコマンドを作成
    cmd1 = assembly.new_cmd("qiime command1")
    cmd1.add_output("out", "file1.qza")
    cmd2 = assembly.new_cmd("qiime command2")
    cmd2.add_input("in", "file1.qza")

    try:
        assembly.sort_commands()
        assert False, "孤立したコマンドが検出されるべき"
    except IsolatedCommandError as e:
        error_msg = str(e)
        assert error_msg.startswith("孤立したコマンドが検出されました")
        assert "qiime isolated-command" in error_msg


def test_is_equal():
    """is_equalメソッドのテスト"""
    cmd1 = (
        Q2CmdAssembly()
        .new_cmd("cmd")
        .add_input("in", "file.qza")
        .add_output("out", "out.qza")
    )
    cmd2 = (
        Q2CmdAssembly()
        .new_cmd("cmd")
        .add_input("in", "file.qza")
        .add_output("out", "out.qza")
    )
    cmd3 = (
        Q2CmdAssembly()
        .new_cmd("cmd")
        .add_input("in", "different.qza")
        .add_output("out", "out.qza")
    )

    assert cmd1 == cmd2
    assert not cmd1 == cmd3  # 内容が異なる場合


def test_build_all():
    assembly = Q2CmdAssembly()

    cmd1 = assembly.new_cmd("qiime cmd1")
    cmd1.add_input("in", "input1.qza")
    cmd1.add_output("out", "output1.qza")

    cmd2 = assembly.new_cmd("qiime cmd2")
    cmd2.add_input("in", "output1.qza")
    cmd2.add_output("out", "output2.qza")

    built_commands = assembly.build_all()
    assert built_commands == [
        ["qiime", "cmd1", "--i-in", "input1.qza", "--o-out", "output1.qza"],
        ["qiime", "cmd2", "--i-in", "output1.qza", "--o-out", "output2.qza"],
    ]
