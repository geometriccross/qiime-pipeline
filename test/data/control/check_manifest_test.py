from tempfile import NamedTemporaryFile
from scripts.data.control.check_manifest import check_manifest


def test_can_currentry_check():
    with NamedTemporaryFile(
        mode="w", suffix=".tsv", delete=True, encoding="utf-8"
    ) as f:
        f.write(
            "id\tforward-absolute-filepath\treverse-absolute-filepath\n"
            "1\tt1_R1.fastq.gz\tt1_R2.fastq.gz\n"
            "2\tt2_R1.fastq.gz\tt2_R2.fastq.gz\n"
        )

        assert check_manifest(f.name) is True
