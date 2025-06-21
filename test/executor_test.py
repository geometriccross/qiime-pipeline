import pytest
import docker
from scripts.executor import Executor


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


@pytest.mark.slow
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
