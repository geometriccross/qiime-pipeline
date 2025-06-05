import docker
from typing import Callable
from scripts.executor import Executor, CommandRunner


def test_executor_create_instance(
    container: Callable[[str], docker.models.containers.Container],
):
    ctn = container("alpine")

    executor = Executor(ctn)
    assert isinstance(executor, Executor)
    assert executor.status() == "created"


def test_container_status_is_currentry_changed(
    container: Callable[[str], docker.models.containers.Container],
):
    ctn = container("alpine")
    executor = Executor(ctn)
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
