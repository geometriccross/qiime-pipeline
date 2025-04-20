#!/usr/bin/env python
import docker
import os
from pathlib import Path
import pytest


@pytest.fixture(scope="session")
def container():
    client = docker.from_env()
    image_tag = "python"
    container = client.containers.run(
        image=image_tag,
        command="sleep infinity",
        detach=True,
        tty=True,
        auto_remove=True,
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
    # 前処理ステップ: create_Mfiles.pyとcheck_manifest.pyの実行
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
    result2 = container.exec_run(["python", "/scripts/check_manifest.py", "/tmp/mani"])
    assert (
        result2.exit_code == 0
    ), f"check_manifest.py failed: {result2.output.decode()}"
    try:
        yield container
    finally:
        container.stop()
