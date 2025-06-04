import docker


class Executor:
    def __init__(self, container: docker.models.containers.Container):
        self.__container = container

    def __enter__(self):
        """コンテナの起動"""
        self.__container.start()
        return CommandRunner(self.__container,)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテナの停止"""
        try:
            self.__container.stop()
        # コンテナが既に削除されている場合は無視
        except docker.errors.NotFound:
            pass

    def status(self) -> str:
        """コンテナのステータスを取得"""
        self.__container.reload()
        return self.__container.status


class CommandRunner:
    def __init__(self, container: docker.models.containers.Container):
        self.__container = container

    def run(self, command: str):
        """コマンドを実行する"""
        exec_id = self.__container.client.api.exec_create(self.__container.id, command)
        output = self.__container.client.api.exec_start(exec_id)
        return output.decode("utf-8")
