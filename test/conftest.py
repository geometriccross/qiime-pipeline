import pytest
import docker


@pytest.fixture
def container():
    def _container(image: str) -> docker.models.containers.Container:
        client = docker.from_env()
        return client.containers.create(image, command="tail -f /dev/null")

    return _container
