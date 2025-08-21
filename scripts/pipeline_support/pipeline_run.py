import datetime
import random
import string
from argparse import Namespace
from scripts.data_store.setting_data_structure import SettingData
from scripts.data_store.dataset import Datasets, Dataset
from scripts.data_store.ribosome_regions import V3V4
from .parse_arguments import argument_parser
from scripts.pipeline_support.executor import Executor, Provider


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


def pipeline_run(runner):
    runner.run("echo hoge")


if __name__ == "__main__":
    args = argument_parser().parse_args()
    setting_data = SettingData(
        workspace_path=args.workspace,
        dockerfile=args.dockerfile,
        datasets=setup_datasets(args),
    )

    # 設定データを保存
    setting_data.write(args.output / "settings.toml")

    provider = Provider.from_dockerfile(
        setting_data.dockerfile,
        mounts=setting_data.datasets.mounts,
        workspace=setting_data.workspace_path,
        remove=True,
    )

    with Executor(provider.provide()) as runner:
        pipeline_run(runner)
