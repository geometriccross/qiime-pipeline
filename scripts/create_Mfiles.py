#!/usr/bin/env python

import re
import csv
import argparse
from textwrap import dedent
from glob import glob
from pathlib import Path, PurePath


# queryで渡されたidを持つfastqファイルを返す
def search_fastq(q: str, data: list[str]) -> tuple[str]:
    correct = []
    for d in data:
        file_name = PurePath(d).name
        if re.match(f"^{q.upper()}_", file_name.upper()):
            correct.append(d)

    # R1, R2以外に名前がかぶっているfastqファイルがあったら
    if len(correct) > 2:
        raise SyntaxError(
            dedent(
                f"""
            同名のファイルが3つ以上存在しています。\n
            {correct}
        """
            )
        )

    fwd = list(filter(lambda s: s.__contains__("_R1_"), correct)).pop()
    rvs = list(filter(lambda s: s.__contains__("_R2_"), correct)).pop()

    fwd_abs_path = Path(fwd).absolute().__str__()
    rvs_abs_path = Path(rvs).absolute().__str__()
    return fwd_abs_path, rvs_abs_path


def get_header(meta_path: str) -> list[str]:
    """
    指定されたメタデータファイルのヘッダーを取得する
    """
    assert Path(meta_path).exists(), f"{meta_path} does not exist"
    with Path(meta_path).open() as f:
        header_str = f.readline().replace("\n", "")
        return header_str.replace("#", "").replace("SampleID", "RawID").split(",")


def header_replaced(header_arr: list[str], id_prefix) -> list[list[str]]:
    # csv writerowsで正常に書き込むためには二次元配列でなければならない
    return [
        [
            id_prefix,
            header_arr[0].replace("SampleID", "RawID").replace("#", ""),
            *header_arr[1:],
        ]
    ]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--id-prefix",
        default="id",
        help=dedent(
            """
            set prefix id of each sample like this [REPLACE THIS] + numeric
            (default : %(default)s))
            """
        ).strip(),
    )
    parser.add_argument("--input-meta", default="/meta")
    parser.add_argument("--input-fastq", default="/fastq")
    parser.add_argument(
        "--out-meta",
        help=dedent(
            """
            output path to metadata
            """
        ).strip(),
    )
    parser.add_argument(
        "--out-mani",
        help=dedent(
            """
            output path to manifest file
            """
        ).strip(),
    )
    parser.add_argument(
        "--meta-fastq-pair",
        help=dedent(
            """
            set a DICTIONARY metadata and fastq file pathes as a pair.
            e.g. --meta-fastq-pair {meta: /foo/bar/metafile.csv,/hoge/huga/fastqdir}
            """
        ).strip(),
    )

    # 引数から取得
    args = parser.parse_args()
    id_prefix = args.id_prefix
    input_meta = args.input_meta
    input_fastq = args.input_fastq
    out_meta = args.out_meta
    out_mani = args.out_mani
    # 引数のdefaultで指定してないのは、その段階ではまだ割り当てられていないinput_metaを使いたかったから

    pair_data = args.meta_fastq_pair
    data_list = (
        pair_data
        if pair_data is not None
        else [
            {"meta": f"{input_meta}/bat_fleas.csv", "fastq": f"{input_fastq}/batfleas"},
            {"meta": f"{input_meta}/cat_fleas.csv", "fastq": f"{input_fastq}/catfleas"},
            {"meta": f"{input_meta}/lip_forti.csv", "fastq": f"{input_fastq}/sk"},
            {
                "meta": f"{input_meta}/mky_louse.csv",
                "fastq": f"{input_fastq}/monkeylice",
            },
        ]
    )

    mani_result = [
        ["sample-id", "forward-absolute-filepath", "reverse-absolute-filepath"]
    ]
    master_list = header_replaced(get_header(data_list[0]["meta"]), id_prefix)

    id_index = 1
    for pair in data_list:
        fastq_pathes = glob(pair["fastq"] + "/**/*.fastq*", recursive=True)
        with open(Path(pair["meta"]).absolute(), "r") as f:
            reader = csv.reader(f)
            header_removed = [row for row in reader][1:]
            for row in header_removed:
                # master csv
                master_list.append([id_prefix + id_index.__str__(), *row])

                # manifest
                # 1列目にあるRawIDから対応するfastqファイルを取得
                mani_result.append(
                    [
                        id_prefix + id_index.__str__(),
                        *search_fastq(row[0], fastq_pathes),
                    ]
                )

                id_index += 1

    with open(out_meta, "w") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerows(master_list)

    with open(out_mani, "w") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerows(mani_result)
