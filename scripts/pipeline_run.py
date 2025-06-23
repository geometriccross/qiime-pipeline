import os
import datetime
import random
import string
from pathlib import Path
import docker
from scripts.executor import Executor


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


def mounts() -> list[docker.types.Mount]:
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


def pipeline_run():
    pipeline_ctn = provid_container()
    with Executor(pipeline_ctn) as executor:
        yield executor
