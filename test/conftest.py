import pytest
import docker


@pytest.fixture
def container():
    def _container(image: str) -> docker.models.containers.Container:
        client = docker.from_env()
        return client.containers.create(image, command="tail -f /dev/null")

    return _container


@pytest.fixture(autouse=True)
def cleanup_containers():
    yield
    # テスト完了後、残存するコンテナを確実に削除
    client = docker.from_env()
    for container in client.containers.list(all=True):
        try:
            container.remove(force=True)
        except docker.errors.APIError:
            pass
