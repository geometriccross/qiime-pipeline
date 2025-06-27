import json
import datetime
import random
import string
from pathlib import Path
import docker
from scripts.executor import Executor
from scripts.data_control.dataset import Databank
from scripts.data_control.used_data import used_data


def generate_id() -> str:
    """
    Generate a unique ID string in the format: 'mmddHHMMSS_xyz'
    where mm is the month name (lowercase), dd is the day,
    HHMMSS is the time, and xyz is a random 3-character string.

    Returns:
        str: Generated ID string
    """
    now = datetime.datetime.now()
    month = now.strftime("%b").lower()
    datetime_str = now.strftime("%d%H%M%S")

    # Generate random 3 characters (lowercase alphanumeric)
    chars = string.ascii_lowercase + string.digits
    random_str = "".join(random.choices(chars, k=3))

    return f"{month}{datetime_str}_{random_str}"


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
        )
    ]


def provid_container():
    docker_client = docker.from_env()
    pipeline_img, _ = docker_client.images.build(
        path=".",
        dockerfile="Dockerfile",
        tag="qiime",
    )
    return docker_client.containers.run(
        pipeline_img, detach=True, remove=False, name="qiime_container"
    )


def data_specification(saved_json_path: Path | None) -> callable[Path, [Databank]]:
    """保存したjsonファイルからデータセットを読み込み、Databankを返す
    もしファイルが存在しない場合は、デフォルトのデータを返す。

    Args:
        saved_json_path (Path | None): 保存されたjsonファイルのパス
    """
    if saved_json_path is None or not saved_json_path.exists():
        return lambda path: used_data(path)
    else:
        json_data = json.load(saved_json_path.read_text())
        return lambda _: Databank.from_json(json_data)


def pipeline_run():
    pipeline_ctn = provid_container()
    with Executor(pipeline_ctn) as executor:
        yield executor
