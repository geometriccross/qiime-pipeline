from pathlib import Path
from typing import Tuple
from argparse import Namespace
from scripts.data.control.check_manifest import check_manifest
from scripts.data.control.create_Mfiles import create_Mfiles
from scripts.data.store.dataset import Datasets, Dataset
from scripts.data.store.setting_data_structure import SettingData
from scripts.data.store.ribosome_regions import V3V4
from scripts.pipeline.support.executor import Executor, Provider
from scripts.pipeline.support.parse_arguments import argument_parser
from typing import Generator


def setup_files(output: Path, datasets: Datasets) -> Tuple[Path, Path]:
    create_Mfiles(
        id_prefix="id",
        out_meta=(metafile := output / "metadata.csv"),
        out_mani=(manifest := output / "manifest.csv"),
        data=datasets,
    )

    if not check_manifest(manifest):
        raise ValueError("Manifest file is invalid")

    return Path(metafile), Path(manifest)


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


def setup() -> Generator[tuple[SettingData, Executor], None, None]:
    args = argument_parser().parse_args()
    setting_data = SettingData(
        workspace_path=args.workspace,
        dockerfile=args.dockerfile,
        datasets=setup_datasets(args),
    )

    # 設定データを保存
    setting_data.write(args.output / "settings.toml")

    provider = Provider(image="quay.io/qiime2/amplicon:2024.10")

    # provider = Provider.from_dockerfile(
    #     setting_data.dockerfile,
    #     mounts=setting_data.datasets.mounts,
    #     workspace=setting_data.workspace_path,
    #     remove=True,
    # )

    yield setting_data, Executor(provider.provide())
