import pytest
import docker
from scripts.executor import Executor, Provider
from python_on_whales import Container


@pytest.fixture(scope="session")
def shared_container():
    client = docker.from_env()
    container = client.containers.create("alpine", command="tail -f /dev/null")
    container.start()  # セッション開始時に1回だけ起動
    yield container
    try:
        container.stop()
        container.remove(force=True)
    except docker.errors.APIError:
        pass


def test_provider():
    provider = Provider(image="alpine")
    assert isinstance(provider, Provider)
    assert isinstance(provider.provide(), Container)


@pytest.mark.parametrize("remove, expected", [(False, "exited"), (True, "absent")])
def test_provider_container_status(remove, expected):
    container = Provider(image="alpine", remove=remove).provide()

    assert Provider.get_status(container) == "running"
    container.stop()
    assert Provider.get_status(container) == expected


def test_executor_lifecycle(shared_container):
    executor = Executor(shared_container)
    assert isinstance(executor, Executor)
    assert executor.status() == "running"
    executor.__exit__(None, None, None)
    assert executor.status() == "exited"


@pytest.mark.slow
@pytest.mark.parametrize(
    "command,expected",
    [
        ("echo Hello, World!", "Hello, World!"),
        ("pwd", "/"),
    ],
)
def test_command_execution(shared_container, command, expected):
    with Executor(shared_container) as executor:
        output = executor.run(command)
        assert output == expected
