from scripts.executor import Executor


def test_executor_create_instance():
    """Executorクラスのインスタンス化テスト"""

    # Executorのインスタンスを作成
    executor = Executor()

    # インスタンスが正しく作成されたか確認
    assert isinstance(executor, Executor)
