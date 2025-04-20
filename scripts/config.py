from typing import TypedDict


class DataSource(TypedDict):
    meta: str
    fastq: str


DATA_LIST: list[DataSource] = [
    {"meta": "meta/bat_fleas.csv", "fastq": "fastq/batfleas"},
    {"meta": "meta/cat_fleas.csv", "fastq": "fastq/catfleas"},
    {"meta": "meta/lip_forti.csv", "fastq": "fastq/sk"},
    {"meta": "meta/mky_louse.csv", "fastq": "fastq/monkeylice"},
]

DEFAULT_ID_PREFIX = "id"
DEFAULT_META_DIR = "/meta"
DEFAULT_FASTQ_DIR = "/fastq"
