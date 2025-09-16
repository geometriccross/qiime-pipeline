from os import getenv
import subprocess
import pytest
from dotenv import load_dotenv
from argparse import Namespace
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import Generator
from scripts.pipeline.support import Provider
from scripts.data.store import (
    Dataset,
    Datasets,
    Region,
    Regions,
    SettingData,
    ContainerData,
)


@pytest.fixture()
def temporay_files():
    with TemporaryDirectory() as fastq_dir:
        with NamedTemporaryFile(delete=True) as metadata_file:
            yield {"fastq": Path(fastq_dir), "meta": Path(metadata_file.name)}


@pytest.fixture()
def temporary_dataset(temporay_files):
    with NamedTemporaryFile(delete=True) as temp_meta:
        temp_meta.write(b"#SampleID,feature1,feature2\n")
        temp_meta.write(b"id1,abc,def\n")
        temp_meta.flush()
        temporay_files["meta"] = Path(temp_meta.name)

        dataset = Dataset(
            name="test_dataset",
            fastq_folder=temporay_files["fastq"],
            metadata_path=temporay_files["meta"],
            region=Region("SampleRegion", 0, 0, 0, 0),
        )
        yield dataset


@pytest.fixture(scope="module")
def trusted_provider():
    provider = Provider(image="alpine", remove=True)

    yield provider


def check_test_data_exist(store_folder: Path) -> bool:
    if not store_folder.exists():
        return False

    result = []
    for folder in store_folder.iterdir():
        if folder.is_file():
            continue

        files_str = "".join([p.name for p in folder.iterdir()])
        result.append("_R1" in files_str)
        result.append("_R2" in files_str)
        result.append("metadata.csv" in files_str)

    return all(result)


def get_ids() -> dict[str, str]:
    load_dotenv()
    dic = {}
    for item in getenv("GOOGLE_DRIVE_TEST_DATA_IDS").split(","):
        key, value = item.split(":")
        dic[key] = value

    return dic


def download_test_data(store_folder: Path):
    store_folder.mkdir(exist_ok=True)
    for sample_name, file_id in get_ids().items():
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        tar_file = str(Path("/tmp") / f"{sample_name}.tar")
        subprocess.run(["wget", url, "-O", tar_file])
        subprocess.run(
            [
                "tar",
                "-xf",
                tar_file,
                "-C",
                str(store_folder),
            ]
        )


@pytest.fixture
def data_path_pairs() -> Generator[list[tuple[Path, Path]], None, None]:
    """
    以下の構造を持つ一時ディレクトリを作成する
    使用後はこれらのファイルは削除される

    <一時ディレクトリ>/
        ├─ test1/
        │  ├─ R1.fastq
        │  ├─ R2.fastq
        │  └─ metadata.csv
        ├─ test2/
        │  ├─ R1.fastq
        │  ├─ R2.fastq
        │  └─ metadata.csv
        ├─ test3/
        │  ├─ R1.fastq
        │  ├─ R2.fastq
        │  └─ metadata.csv
        └─ test4/
           ├─ R1.fastq
           ├─ R2.fastq
           └─ metadata.csv

    Returns:
        List[Tuple[Path, Path]]

        metadataとfastqファイルの入ったフォルダの組み合わせ。
        以下のようなデータが返される

        **[(test1/metadata.csv,test1),(test2/metadata.csv,test2),...]**
    """

    store_path = Path("/tmp/qiime_pipeline_test_data")
    if check_test_data_exist(store_path) is False:
        download_test_data(store_path)

    # namespaceにすぐに渡せるよう、metadataとfastq_folderの組み合わせを作っておく
    yield [
        (sample_dir / "metadata.csv", sample_dir) for sample_dir in store_path.iterdir()
    ]


@pytest.fixture
def dummy_datasets(
    data_path_pairs: list[tuple[Path, Path]],
) -> Generator[Datasets, None, None]:
    """
    data_path_pairsを使ってDatasetsオブジェクトを作成する

    Returns:
        Datasets: data_path_pairsの内容を持つDatasetsオブジェクト
    """
    sets = set()
    for meta, folder in data_path_pairs:
        sets.add(
            Dataset(
                name=folder.name,
                fastq_folder=folder,
                metadata_path=meta,
                region=Regions()["V3V4"],
            )
        )

    yield Datasets(sets=sets)


@pytest.fixture
def namespace(data_path_pairs) -> Namespace:
    with Path(TemporaryDirectory().name) as temp_host_dir:
        return Namespace(
            data=data_path_pairs,
            dataset_region="V3V4",
            image="quay.io/qiime2/amplicon:latest",
            dockerfile=Path("dockerfiles/Dockerfile"),
            local_output=Path(temp_host_dir / "output"),
            local_database=Path("db/classifier.qza"),
            sampling_depth=5,
        )


@pytest.fixture
def setting(namespace, dummy_datasets) -> SettingData:
    ctn_data = ContainerData(
        image_or_dockerfile=namespace.image,
        workspace_path=namespace.workspace_path,
        output_path=namespace.output,
        database_path=namespace.database,
    )

    return SettingData(
        container_data=ctn_data,
        sampling_depth=namespace.sampling_depth,
        datasets=dummy_datasets,
    )
