import pytest
import docker
from typing import Callable
from scripts.executor import Executor, CommandRunner


@pytest.fixture(autouse=True, scope="session")
def cleanup_containers():
    yield
    # テスト完了後、残存するコンテナを確実に削除
    client = docker.from_env()
    for container in client.containers.list(all=True):
        try:
            container.remove(force=True)
        except docker.errors.APIError:
            pass


def test_executor_create_instance_and_currently_spend_a_lifecycle(
    container: Callable[[str], docker.models.containers.Container],
):
    ctn = container("alpine")

    executor = Executor(ctn)
    assert isinstance(executor, Executor)
    assert executor.status() == "created"
    executor.__enter__()
    assert executor.status() == "running"
    executor.__exit__(None, None, None)
    assert executor.status() == "removing" or executor.status() == "exited"


def test_executor_return_command_runner_when_enter_with_statement(
    container: Callable[[str], docker.models.containers.Container],
):
    with Executor(container("alpine")) as executor:
        assert isinstance(executor, CommandRunner)
        assert hasattr(executor, "run")
        assert callable(executor.run)


def test_executor_run_commands(
    container: Callable[[str], docker.models.containers.Container],
):
    with Executor(container("alpine")) as executor:
        output = executor.run("echo Hello, World!")
        assert output == "Hello, World!"
