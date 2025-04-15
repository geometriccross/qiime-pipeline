import csv
import argparse
from textwrap import dedent

parser = argparse.ArgumentParser(
    description="指定した列の値に基づいて、CSVデータの行を抽出または除外します。"
)
parser.add_argument(
    "input_path",
    help=dedent("""
        データ、メタデータ、またはマニフェストのファイルパス
        """)
)
parser.add_argument(
    "targets",
    nargs="+",
    help=dedent("""
        抽出対象のID（複数指定可）
        """)
)
parser.add_argument(
    "-c", "--column",
    type=int,
    default=0,
    help=dedent("""
        対象とする列のインデックス（0始まり）
        """)
)
parser.add_argument(
    "-r",
    "--exclude",
    action="store_true",
    help=dedent("""
        このオプションが指定された場合、ターゲットIDに一致する行を除外します。
        （指定がない場合は、一致する行のみを出力します）
        """)
)

args = parser.parse_args()

with open(args.input_path, newline="") as file:
    reader = csv.reader(file, delimiter="\t")
    header = next(reader)
    output_lines = ["\t".join(header)]
    for row in reader:
        # 列数が足りない行はスキップ
        if len(row) <= args.column:
            continue
        # 指定された列の値がターゲットに含まれているかどうか
        match = row[args.column] in args.targets
        if args.exclude:
            if not match:
                output_lines.append("\t".join(row))
        else:
            if match:
                output_lines.append("\t".join(row))

print("\n".join(output_lines))
