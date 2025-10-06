from pathlib import Path
import argparse


def parse_pair(pair: str) -> tuple[Path, Path]:
    """Parse a string of the form 'metadata_path:fastq_folder' into a tuple of Paths."""
    if ":" not in pair:
        raise ValueError(
            f"Invalid pair format: {pair}. Expected 'metadata_path:fastq_folder'."
        )

    metadata_path_str, fastq_folder_str = pair.split(":")

    if not metadata_path_str or not fastq_folder_str:
        raise ValueError(
            f"""Invalid pair format: {pair}.
                Both metadata path and fastq folder must be provided."""
        )

    return Path(metadata_path_str.strip()), Path(fastq_folder_str.strip())


def argument_parser():
    """Create and return an argument parser for the QIIME pipeline."""
    parser = argparse.ArgumentParser(description="Run the QIIME pipeline.")
    parser.add_argument(
        "--data",
        type=parse_pair,
        nargs="+",
        help="""
            Pairs of fastq and metadata paths to use for the pipeline.
            Example:
                --data path/to/metadata_path:path/to/fastq_folder,
                       path/to/another_metadata:path/to/another_fastq_folder
            """,
    )
    parser.add_argument(
        "--dataset-region",
        type=str,
        default="V3V4",
        help="Region of the 16S rRNA gene for the dataset (default: V3V4).",
    )
    parser.add_argument(
        "--image",
        type=str,
        default="quay.io/qiime2/amplicon:2024.10",
        help="Docker image to use for the QIIME pipeline.",
    )
    parser.add_argument(
        "--dockerfile",
        type=Path,
        default=Path("Dockerfile"),
        help="Path to the Dockerfile for building the container.",
    )
    parser.add_argument(
        "--local-output",
        type=Path,
        default=Path("./out"),
        help="Output directory for the results.",
    )
    parser.add_argument(
        "--local-database",
        type=Path,
        default=Path("./classifier.qza"),
        help="Path to the local database file.",
    )
    parser.add_argument(
        "--sampling_depth",
        type=int,
        default=10000,
    )

    return parser
