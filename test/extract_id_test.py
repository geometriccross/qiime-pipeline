#!/usr/bin/env python
import docker
import os
import pytest
import time
from pathlib import Path


@pytest.fixture(scope="function")
def container():
    client = docker.from_env()
    image_tag = "python"
    container_name = f"extract_id_test_{int(time.time())}"

    # コンテナの起動
    container = client.containers.run(
        image=image_tag,
        name=container_name,
        command="sleep infinity",
        detach=True,
        tty=True,
        mounts=[
            docker.types.Mount(
                target="/meta",
                source=Path("./meta").absolute().__str__(),
                type="bind",
                read_only=True,
            ),
            docker.types.Mount(
                target="/fastq",
                source=Path("./fastq").absolute().__str__(),
                type="bind",
                read_only=True,
            ),
            docker.types.Mount(
                target="/scripts",
                source=os.path.abspath("scripts"),
                type="bind",
                read_only=True,
            ),
        ],
    )

    # ------ 前処理の2ステップ ------
    # 1. create_Mfiles.py
    result1 = container.exec_run(
        [
            "python",
            "/scripts/create_Mfiles.py",
            "--id-prefix",
            "id",
            "--out-meta",
            "/tmp/meta",
            "--out-mani",
            "/tmp/mani",
        ]
    )

    assert result1.exit_code == 0, f"create_Mfiles.py failed: {result1.output.decode()}"

    # 2. check_manifest.py
    result2 = container.exec_run(["python", "/scripts/check_manifest.py", "/tmp/mani"])
    assert (
        result2.exit_code == 0
    ), f"check_manifest.py failed: {result2.output.decode()}"

    try:
        yield container  # テスト関数にコンテナを提供
    finally:
        container.remove(force=True)


@pytest.mark.parametrize("extract", [["id1", "id2", "id21", "id25"]])
def test_extract_correctry(container, extract):
    cmd = ["python", "/scripts/extract_id.py", "/tmp/meta"] + extract

    result = container.exec_run(cmd=cmd, demux=True)
    stdout, stderr = result.output

    output = stdout.decode() if stdout else ""
    assert all(id_ in output for id_ in extract), f"Expected IDs not found: {output}"


@pytest.mark.parametrize(
    "pattern",
    [
        {"target": ["ctenocephalides_felis"], "origin": ["meta/cat_fleas.csv"]},
        {
            "target": ["ctenocephalides_felis", "ischnopsyllus_needhami"],
            "origin": ["meta/cat_fleas.csv", "meta/bat_fleas.csv"],
        },
    ],
)
def test_column_based_extract(container, pattern):
    target = pattern["target"]
    origin = pattern["origin"]
    cmd = ["python", "/scripts/extract_id.py", "/tmp/meta", "--column", "3"] + target

    result = container.exec_run(cmd=cmd, demux=True)
    stdout, stderr = result.output
    output = stdout.decode() if stdout else ""

    total_line = 0 if len(origin) <= 1 else -1  # count header
    for path in origin:
        with open(path, "r") as f:
            total_line += len(f.readlines())

    for target in target:
        assert target in output
        assert total_line == output.count("\n")
