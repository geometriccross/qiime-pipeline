from argparse import Namespace
from scripts.data.store.setting_data_structure import SettingData
from scripts.data.store.dataset import Datasets, Dataset
from scripts.data.store.ribosome_regions import V3V4
from .parse_arguments import argument_parser
from .executor import Executor, Provider, CommandRunner
from typing import Generator


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


def setup() -> Generator[CommandRunner, None, None]:
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
        yield runner
