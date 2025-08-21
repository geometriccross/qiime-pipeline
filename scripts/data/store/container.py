import docker
from pathlib import Path


def mounts(data_path: Path) -> list[docker.types.Mount]:
    """

    Args:
        data_path (Path): ホスト側に存在するfastqやmetadataが格納されているディレクトリのパス

    Returns:
        list[docker.types.Mount]: Dockerコンテナにマウントするための設定リスト
    """
    return [
        docker.types.Mount(
            target="/data",
            source=data_path.absolute().__str__(),
            type="bind",
            read_only=True,
        ),
    ]


def provid_container(dockerfile: Path) -> docker.models.containers.Container:
    docker_client = docker.from_env()
    pipeline_img, _ = docker_client.images.build(
        dockerfile=dockerfile,
        tag="qiime",
    )
    return docker_client.containers.run(
        pipeline_img, detach=True, remove=False, name="qiime_container"
    )
