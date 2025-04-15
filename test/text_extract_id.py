#!/usr/bin/env python
import docker
import os
import pytest
import tempfile
import time


@pytest.fixture(scope="function")
def docker_container():
    client = docker.from_env()
    image_tag = "qiime"
    container_name = f"extract_id_test_{int(time.time())}"

    # 一時ディレクトリの作成
    with tempfile.TemporaryDirectory() as temp_dir:
        # テストデータの配置
        meta_src = os.path.abspath("test/assets/meta")
        meta_dst = os.path.join(temp_dir, "meta")
        os.system(f"cp {meta_src} {meta_dst}")

        # コンテナの起動
        container = client.containers.run(
            image=image_tag,
            name=container_name,
            command="sleep infinity",
            detach=True,
            tty=True,
            mounts=[
                docker.types.Mount(
                    target="/tmp",
                    source=temp_dir,
                    type="bind"
                ),
                docker.types.Mount(
                    target="/scripts",
                    source=os.path.abspath("scripts"),
                    type="bind",
                    read_only=True
                ),
            ]
        )

        # ------ 前処理の2ステップ ------
        # 1. create_Mfiles.py
        result1 = container.exec_run([
            "python", "/scripts/create_Mfiles.py",
            "--id-prefix", "id",
            "--out-meta", "/tmp/meta",
            "--out-mani", "/tmp/mani"
        ])
        assert result1.exit_code == 0, f"create_Mfiles.py failed: {
            result1.output.decode()}"

        # 2. check_manifest.py
        result2 = container.exec_run(
            ["python", "/scripts/check_manifest.py", "/tmp/mani"])
        assert result2.exit_code == 0, f"check_manifest.py failed: {
            result2.output.decode()}"

        try:
            yield container  # テスト関数にコンテナを提供
        finally:
            container.remove(force=True)
