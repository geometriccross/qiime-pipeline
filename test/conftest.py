#!/usr/bin/env python
import os
import uuid
import docker
import pytest
import shutil
from pathlib import Path
from typing import Generator


def create_temp_dir() -> Path:
    """一時ディレクトリを作成する

    Returns:
        Path: 作成された一時ディレクトリのパス
    """
    tmp_dir = Path("/tmp") / str(uuid.uuid4())
    tmp_dir.mkdir(parents=True, exist_ok=False)
    return tmp_dir


def get_docker_mounts() -> list[docker.types.Mount]:
    """Dockerコンテナのマウント設定を取得する

    Returns:
        list[docker.types.Mount]: マウント設定のリスト
    """
    return [
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
    ]


def create_docker_container(
    image: str,
    client: docker.DockerClient,
    mounts: list[docker.types.Mount] = [],
) -> docker.models.containers.Container:
    """Dockerコンテナを作成する

    Args:
        image: 使用するDockerイメージ名
        client: Dockerクライアント
        mounts: コンテナにマウントするディレクトリのリスト

    Returns:
        Container: 作成されたDockerコンテナ
    """
    return client.containers.run(
        image=image,
        command="sleep infinity",
        detach=True,
        tty=True,
        auto_remove=True,
        mounts=mounts,
    )


def execute_container_command(
    container: docker.models.containers.Container,
    command: list[str],
    error_message: str,
) -> None:
    """コンテナ内でコマンドを実行し、エラーチェックを行う

    Args:
        container: Dockerコンテナ
        command: 実行するコマンド
        error_message: エラー時のメッセージ

    Raises:
        AssertionError: コマンドが失敗した場合
    """
    result = container.exec_run(command)
    assert result.exit_code == 0, f"{error_message}: {result.output.decode()}"


@pytest.fixture
def tmp_path() -> Generator[Path, None, None]:
    """テスト用の一時ディレクトリを提供する"""
    tmp_dir = create_temp_dir()
    yield tmp_dir
    shutil.rmtree(tmp_dir)


@pytest.fixture(scope="session")
def container() -> Generator[docker.models.containers.Container, None, None]:
    """基本的なDockerコンテナを提供する"""
    client = docker.from_env()
    container = create_docker_container(client)
    try:
        yield container
    finally:
        container.stop()


@pytest.fixture(scope="session")
def modified_container() -> Generator[docker.models.containers.Container, None, None]:
    """前処理が実行されたDockerコンテナを提供する"""
    client = docker.from_env()
    container = create_docker_container(client)

    # 前処理ステップの実行
    execute_container_command(
        container,
        [
            "python",
            "/scripts/create_Mfiles.py",
            "--id-prefix",
            "id",
            "--out-meta",
            "/tmp/meta",
            "--out-mani",
            "/tmp/mani",
        ],
        "create_Mfiles.py failed",
    )

    execute_container_command(
        container,
        ["python", "/scripts/check_manifest.py", "/tmp/mani"],
        "check_manifest.py failed",
    )

    try:
        yield container
    finally:
        container.stop()
