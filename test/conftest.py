import pytest
from argparse import Namespace
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from textwrap import dedent
from typing import Generator
from scripts.pipeline.support import Provider
from scripts.data.store import (
    Dataset,
    Datasets,
    Region,
    V3V4,
    SettingData,
    ContainerData,
    PairPath,
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

    data = {
        "test1": {
            "R1": dedent(
                """\
                @M04013:78:000000000-D5GWH:1:1101:14962:1734 1:N:0:CGTACTAG+TATTCTCT
                CCTACGGGCGGCAGCAGTGGGGAATATTGGACAATGGGCGCAAGCCTGATCCAGCAATACCGCGTGTGCGATGAAGGCCTTCGGGTTGTAAAGCTCTTTTAGCAAGGAAGATAATGACGTTACTTGCAGTAATAGCCCCTGCTATCTCCTTTCCAGCAGCCCCGGTATGCCGGTGGGGGCTAGCGTTGTTCGGTCTTACTGGGCGTAACGTGCGTGTAGGTGGTTTAGTTTGTTGGTTGTGAAAGCCCGTG
                +
                BBBBBBBB2D@AAAABFFEGCGCFGFFHB3BG31B3B11EF000FFHF2B3F33B22@3BGE/EEF//4//?/43?B?F?G3?<CGF/C22B2?<FHHH222222?/?0CF1<1@111/?F0>F111111111111</...</00/000000<:00//.:C.;--9-./0:---;.9--9@../-99-9A/.-...;/BF//..-9-..9...-..;.////..;./9////:.9....99/////.9--.
                """
            ),
            "R2": dedent(
                """\
                @M04013:78:000000000-D5GWH:1:1101:14962:1734 2:N:0:CGTACTAG+TATTCTCT
                GACTACTCGGGTATCTAATCCTGTTTGCTCCCCACGCTTTCGTGCCTCCGCGTCAGTTGTTGCCCAGTTCACCGCCTTCGCCACCGGTCTTCCTCCTTATCTCTCCGCATTTCACCTCTACACTTGGCATTCCACCATCCCCTACTACACTCTAGCTTATTAGTTTCCAATGCATTTCCGCGGTTAAGCCCCGGGCTTTCCCCTCTTACTTCCTAAACCCCCTCCGCACTCTTTACGCCCCCTCATTCCG
                +
                11AAAF1CA11A1FGGF1GGGGFGH30DGFFGGBAAEGGGHE0/B/DA/A//AE//B211/01BE1/11221@BEEFGH/EE//0>/>/?FG1BDG012B1BGH10?//?CHD2FGFHHDG1F111101@@G2210/1?F/?G/?1111?FHF1=1<<11111>1=11000<<00<=GH..--;@.00C/.:---;AEGG0C/;E/00;CF0C9///;B-;@@-;---;9FFFF/;-A?@--;--9BFF/
                """
            ),
            "meta": dedent(
                """\
                #SampleID,SampleGender
                test1,male
                """
            ),
        },
        "test2": {
            "R1": dedent(
                """\
                @M04013:78:000000000-D5GWH:1:1101:14975:1748 1:N:0:CGTACTAG+TATTCTCT
                CCTACGGGCGGCAGCAGTGGGGAATATTGGACAATGGGCGCAAGCCTGATCCAGCAATACCGCGTGTGCGATGAAGGCCTTAGGGTTGTAAAGCTCTTTTAGCAAGGAAGATAATGTCGTTACTTGCAGTAAAAGCCCCTGCTAACTCCGTTCCAGCAGCCGCGGTATGACGGTGGGGGCTAGCGTTGTTCGGTATTACTGGGCGTAAAGTTCGCGTAGGCGGTTTAGTATGTTGGATGTGAAAGCCCGGG
                +
                BBBBB?>>>@2AAAABFGGGGGFFGHHHF3FGFGHHGFAEEEE0GGHGGGFHFFG2BB@FGE/>EE/?4?????3BF?FFH3BDCHG@FBDD2BBGHHH222222?/02F<?11@111<?E/FG111<11111110<....<<00/<<0.<0=:00::.:C-=--:../0;.-.9.9--;@..9-::-;E9.-..9;/BF//..-;-..;///.--;--./---;9/99///://.//99://9//99---
                """
            ),
            "R2": dedent(
                """\
                @M04013:78:000000000-D5GWH:1:1101:14975:1748 2:N:0:CGTACTAG+TATTCTCT
                GCCTACTCGGGTCTCTAATCCTGTTTGCTCCCCACGCTTTCGTGCCTCAGCGTCAGTTTTCGCCCAGTTCACCGCCTTCGCCACCGGTCTTCCTCCTAATATCTCAGCATTTCACCTCTACACTTGGAATTCCACCATCCCCTACTACACTCTAGCTTACTAGTTTTCAATGCAATTCCGCGGTTAAGCCCCGGGCTTTCACCTCCAACTTACTAAACCCCCTACGCCCTCTTTACGCCCAGTACTTCCGA
                +
                11>A1C1CA1>A1BGGA1FFGGHHHA0DGFFGGBAAEGGGHE0/B/DA111BEEA/F2222//BE/>1@221@>>EEGH>EE//0//>/?BG1BFG011B2BGH22211BFHF2FGHHHDG1F11<111BFH1210/1@F/?G/GC111?GHH1?1<<11111><=11111=>11<FGH/.--<;.0:;/.::--;AGGG0F0;F.//=CF0;9000;F.C@@-F-9-;@EFFF/B-A@@--;//;BFF--
                """
            ),
            "meta": dedent(
                """\
                #SampleID,SampleGender
                test2,male
                """
            ),
        },
        "test3": {
            "R1": dedent(
                """\
                @M04013:78:000000000-D5GWH:1:1101:15780:1765 1:N:0:CGTACTAG+TATTCTCT
                CCTACGGGCGGCAGCAGTGGGGAATATTGGACAATGGGCGCAAGCCTGATCCAGCTATACCGCGTGTGCGATGAAGGCCTTAGGGTTGTAAAGCTCTTTCAGCAAGGAAGATAATGTCGTTACTTGCAGAAATAGCCCCGGCTATCTCCGTGCCAGCAGCCGCGGTATGACGGAGGGCGCTAGCGTTGTTCGGTATTACTGGGCGTAAAGTGCGTGTAGGCGGTTTTGTATGTTGGATGTGAAAGCCCGGG
                +
                BBBBB?AD???A2AABFGGGGGFEFAGHFBFGHFGHGG1EEEE0BFHHCGDGDFG3BB4FGE/EGG/?4???EF3BG?FFH3BGFHG@GFDF2B1GHHH222110?/<0F0<11@111??EAFF1=1><1011111>0.--<-.0/000.:.;:0:.;::G-A--;../0;.-.9-;.-;@-.9-9;-;A9.-...;/FF//..-;9..;///-..;.///---;9...///://.//;/;/////.9---
                """
            ),
            "R2": dedent(
                """\
                @M04013:78:000000000-D5GWH:1:1101:15780:1765 2:N:0:CGTACTAG+TATTCTCT
                GACTACTAGGGTATCTAATCCTGTTTGCTCCCCACGCTTTCGTGCATCAGCGTCAGTTGTTGCCCAGTTCACCGCCTTCGCCACTGGTCTTCCTCCTAATCTCTCCGCATTTCACCTCTACACTTGGAATTCCACCATCCTCTACTACACTCTAGCTTATTAGTTTCCCATGCATTTCCTACGTTCAGCCTCGGGCTTTCACCTCTAACTTACTAAACCCCCTACGCACTCTTTACGCCCAGTAATTCCG
                +
                11>A1C@3B11C1BGGAAGFGGGHHB0FGFHGGBAEEGGGHC0AB/DB1A1BEE/AF21A/01BF1/1A221AA>EEGHFEE/>1B0B1BFH1BBG011B1BGH10///?EHF2FGHHHFF1F11<111BFH1210/1BF1BG1@2111@GHF1>12>111<1@1?111110?11<FGH111.>F011>0/<<.-<AHHH0G0CG000=CG0C0000;C.CAG.F;9.A@FFGG0C9C@A--;//:BFF/
                """
            ),
            "meta": dedent(
                """\
                #SampleID,SampleGender
                test3,female
                """
            ),
        },
        "test4": {
            "R1": dedent(
                """\
                @M04013:78:000000000-D5GWH:1:1101:12446:1768 1:N:0:CGTACTAT+TTTCCTCT
                CCTACGGGGGGCAGCAGTGGGGAATATTGGACAATGGGGGCAACCCTGATCCAGCCATGCCGCGTGTGTGATGAATGCCTTAGGGTTGTAAAGCTCTTTCTCCGGTGAAGATATTGTCGGTACTCGTAGTTGTAGCCCCTGCTTTCTTCTTTCCAGCAGCCCCTGTATTACGCCGGGCGCTCGCGTTGTTCGGTTTTTCTGGGCGTAAAGCGCATGTAGGCGGTTTTTTATGTCAGTTGTGTATTCC
                +
                >AABBAAD?D?>>??BGGGFCEDGGGGHD33BCCGD10//@CA<FDHFBG1GB<G<0F1FG-C-C-..<.0<00000::0<000.CG-=:0:0;BFFGGB000;-;-.000900;000;-;..//9....////////...9/////9//9/;9///...9.;..9/////..------9;.---99-;E/.-.:9A.;://..-;-..//.9-..;////---;.;E9.//:9/////9..//;//
                """
            ),
            "R2": dedent(
                """\
                @M04013:78:000000000-D5GWH:1:1101:12446:1768 2:N:0:CGTACTAT+TTTCCTCT
                GTCTCCTCTTTTCTCTAATCCTGTTTTCTCCCCACTCTTTCGCTCCTCCGCGTCAGTTTTTTTCCATTTTTCCTCCTTCTCCACTTTTTTTCCTCCTTCTCTCTACTCATTTCACCTCTACCCTCTTCATTCCCCTCTCCTCTTCCTCACTCTCGCCTTCCATTTTCAACTTCATTTCCTCTTTTCAGCCTTTGTCTTTCACCTCTTACTTAATTATCCTCCTTCTCTCTCTTTACTCCCATTACTTCCGT
                +
                11>>1@@1113B3BFG31BAFG1FGF0DGDAFA0A0BFGFH000BAF00///AE//D222///B@22@221011BBFFG1BB10@11B1>>F1B>B011B1BFG2B211BFG22BBGGH1B1B1/0112BBF21<0<0@@@GH1F1111??F11/////1011<1>=11111=11====1000==000<//00000==GG0;:CCC00;;C000000:00:;F00000909;BB009;99/0;000;;9.0
                """
            ),
            "meta": dedent(
                """\
                #SampleID,SampleGender
                test4,female
                """
            ),
        },
    }

    temp_dir = TemporaryDirectory()
    root = Path(temp_dir.name)
    for sample_name, files in data.items():
        sample_dir = root / sample_name
        sample_dir.mkdir()

        for key, content in files.items():
            if key in ("R1", "R2"):
                filename = f"{sample_name}_{key}.fastq"
            else:
                filename = "metadata.csv"
            (sample_dir / filename).write_text(content)

    # namespaceにすぐに渡せるよう、metadataとfastq_folderの組み合わせを作っておく
    yield [(sample_dir / "metadata.csv", sample_dir) for sample_dir in root.iterdir()]
    temp_dir.cleanup()


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
                name=folder.name, fastq_folder=folder, metadata_path=meta, region=V3V4()
            )
        )

    yield Datasets(sets=sets)


@pytest.fixture
def namespace(data_path_pairs) -> Namespace:
    with Path(TemporaryDirectory().name) as temp_host_dir:
        return Namespace(
            data=data_path_pairs,
            image="quay.io/qiime2/amplicon:2024.10",
            dockerfile=Path("dockerfiles/Dockerfile"),
            local_output=Path(temp_host_dir / "output"),
            local_database=Path("db/classifier.qza"),
            sampling_depth=10000,
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
