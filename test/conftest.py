from os import getenv
import subprocess
import pytest
from dotenv import load_dotenv
from argparse import Namespace
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import Generator, Callable
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


def _validate_data_directory(root: Path) -> list[Path]:
    """データディレクトリの基本検証を行い、有効なディレクトリのリストを返す"""
    if not root.exists():
        return []

    return [d for d in root.iterdir() if d.is_dir() and not str(d).endswith(".tar")]


def _check_required_files(data_dir: Path) -> bool:
    """必要なファイルが存在するか検証する"""
    required_files = {"metadata.csv": False, "R1": False, "R2": False}

    for file_path in data_dir.iterdir():
        match file_path.name:
            case "metadata.csv":
                required_files["metadata.csv"] = True
            case name if "_R1" in name:
                required_files["R1"] = True
            case name if "_R2" in name:
                required_files["R2"] = True

    return all(required_files.values())


def check_test_data_exist(root: Path) -> bool:
    """テストデータディレクトリの構造を検証する"""
    data_dirs = _validate_data_directory(root)
    if not data_dirs:
        return False

    return all(_check_required_files(dir_) for dir_ in data_dirs)


def download_test_data(env_var: str, store_folder: Path):
    """
    テストデータをダウンロードして展開する

    Args:
        env_var: 環境変数名（Google DriveのファイルID）
        store_folder: 保存先ディレクトリ

    Raises:
        RuntimeError: ダウンロードまたは展開に失敗した場合
        FileNotFoundError: 必要な環境変数が見つからない場合
    """
    if not load_dotenv():
        raise RuntimeError("Failed to load .env file")

    store_folder.mkdir(exist_ok=True, parents=True)
    file_id = getenv(env_var)
    if not file_id:
        raise FileNotFoundError(f"Environment variable {env_var} not found")

    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    tar_path = store_folder / f"{env_var}.tar"

    # ダウンロード実行
    result = subprocess.run(
        ["wget", url, "-O", tar_path.as_posix()],
        check=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to download test data: {result.stderr.decode()}")

    if not tar_path.exists():
        raise FileNotFoundError(f"Downloaded file not found: {tar_path}")

    # 展開実行
    result = subprocess.run(
        [
            "tar",
            "-xf",
            tar_path.as_posix(),
            "-C",
            store_folder.as_posix(),
        ],
        check=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to extract test data: {result.stderr.decode()}")


@pytest.fixture
def data_path_pairs() -> (
    Callable[[str], Generator[list[tuple[Path, Path]], None, None]]
):
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

    def _data_path_pairs(
        gdrive_env_var: str = "DEFAULT_TEST_DATA",
    ) -> Generator[tuple[Path, Path], None, None]:
        store_path = Path(f"/tmp/qiime_pipeline_test_data/{gdrive_env_var}")
        if check_test_data_exist(store_path) is False:
            download_test_data(gdrive_env_var, store_path)

        # namespaceにすぐに渡せるよう、metadataとfastq_folderの組み合わせを作っておく
        # ディレクトリのみを対象とし、tarファイルは除外
        for sample_dir in store_path.iterdir():
            if not sample_dir.is_dir() or str(sample_dir).endswith(".tar"):
                continue

            yield (sample_dir / "metadata.csv", sample_dir)

    return _data_path_pairs


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
    for meta, folder in data_path_pairs():
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
def namespace(request, data_path_pairs) -> Namespace:
    if request.node.get_closest_marker("gdrive_env_var"):
        gdrive_env_var = request.node.get_closest_marker("gdrive_env_var").args[0]
    else:
        gdrive_env_var = "DEFAULT_TEST_DATA"

    with Path(TemporaryDirectory().name) as temp_host_dir:
        return Namespace(
            data=data_path_pairs(gdrive_env_var),
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
