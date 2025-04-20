#!/usr/bin/env python
import subprocess


def test_check_manifest_valid(container):
    """
    正常なマニフェストファイルを用いた場合、エラーなく終了するかを検証
    """
    result = container.exec_run(
        ["python", "/scripts/check_manifest.py", "/tmp/mani/manifest.txt"]
    )
    manifest_file.write_text("header1,header2\nvalue1,value2")
    cmd = ["python", "scripts/check_manifest.py", str(manifest_file)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, f"Output: {result.stdout} Error: {result.stderr}"


def test_check_manifest_invalid(tmp_path):
    """
    不正なマニフェストファイルを用いた場合、エラーになることを検証
    """
    manifest_file = tmp_path / "invalid_manifest.txt"
    manifest_file.write_text("invalid content")
    cmd = ["python", "scripts/check_manifest.py", str(manifest_file)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode != 0, "Invalid manifest should cause an error"
