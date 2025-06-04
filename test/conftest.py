#!/usr/bin/env python
import os
import uuid
import docker
import pytest
from pathlib import Path


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
    return client.containers.create(
        image=image,
        command="sleep infinity",
        detach=True,
        tty=True,
        auto_remove=True,
        mounts=mounts,
    )


@pytest.fixture()
def container():
    def __container(image: str) -> docker.models.containers.Container:
        client = docker.from_env()
        mounts = []
        return create_docker_container(image, client, mounts)

    return __container
