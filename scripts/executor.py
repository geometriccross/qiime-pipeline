import docker


class Executor:
    def __init__(self, container: docker.models.containers.Container):
        self.__container = container

    def __enter__(self):
        """コンテナの起動"""
        self.__container.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテナの削除"""
        self.__container.stop()

    def status(self) -> str:
        """コンテナのステータスを取得"""
        self.__container.reload()
        return self.__container.status

    def run(self, command: str):
        """コンテナ内でコマンドを実行"""
        exec_id = self.__container.client.api.exec_create(self.__container.id, command)
        output = self.__container.client.api.exec_start(exec_id)
        return output.decode("utf-8")

    def stop(self):
        """コンテナの明示的な停止"""
        self.__container.stop()
