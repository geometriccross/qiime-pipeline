from pathlib import Path
import argparse


def parse_pair(pair_str: str) -> list[tuple[Path, Path]]:
    """Parse a string of the form 'metadata_path:fastq_folder' into a tuple of Paths."""
    result = []
    for pair in pair_str.split(","):
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

        result.append(
            (
                Path(metadata_path_str.strip()),
                Path(fastq_folder_str.strip()),
            )
        )

        return result


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
        "--dockerfile",
        type=Path,
        default=Path("Dockerfile"),
        help="Path to the Dockerfile for building the container.",
    )
    parser.add_argument(
        "--sampling_depth",
        type=int,
        default=10000,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output"),
        help="Output directory for the results.",
    )
    return parser
