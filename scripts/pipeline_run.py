import datetime
import random
import string
from python_on_whales import docker
from pathlib import Path
from argparse import Namespace
from scripts.data_store.setting_data_structure import SettingData
from scripts.data_store.dataset import Datasets, Dataset
from scripts.data_store.ribosome_regions import V3V4
from scripts.data_control.parse_arguments import argument_parser
from scripts.executor import Executor, Provider


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


def setup_datasets(arg: Namespace) -> Datasets:
    data = []
    for metadata_path, fastq_folder in arg.data:
        # Use the basename of the metadata path as the dataset name
        data.append(
            Dataset(
                name=fastq_folder.stem,
                fastq_folder=fastq_folder,
                metadata_path=metadata_path,
                region=V3V4(),
            )
        )

    return Datasets(sets=set(data))


def arg_factory(workdir: Path, command: list[str]) -> dict:
    # docker execではentorypointを経由せず直接コマンドを実行するためbase環境が認識されない
    # そのためexecを使用する際にはbaseを認識させなければならない
    cmd_line = [
        "micromamba",
        "run",
        "-n",
        "base",
        "bash",
        "-exc",
        f'{" ".join(command)}',
    ]

    return {
        "command": " ".join(cmd_line),
        "workdir": workdir,
        "detach": True,
        "remove": True,
    }


def pipeline_run(executor):
    runner.execute()
    executor.execute(
        **arg_factory(
            workdir=setting_data.workspace_path,
            command="qiime --help".split(),
        )
    )


if __name__ == "__main__":
    args = argument_parser().parse_args()
    setting_data = SettingData(
        workspace_path=args.workspace,
        dockerfile=args.dockerfile,
        datasets=setup_datasets(args),
    )

    # 設定データを保存
    setting_data.write(args.output / "settings.toml")

    provider = Provider.from_dockerfile(setting_data.dockerfile, remove=True)
    with Executor(provider.provide()) as runner:
        pipeline_run(runner)
